"""Portable installer regression tests; macOS tools are mocked, not emulated."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).with_name('ps4pkg').read_text().split(
    '# ---------------------------------------------------------------------- main')[0]


class InstallerTests(unittest.TestCase):
    def run_shell(self, commands):
        with tempfile.TemporaryDirectory() as tmp:
            script = SOURCE + '\ncd "$TEST_ROOT"\n' + commands
            return subprocess.run(['bash', '-c', script], text=True,
                capture_output=True, env=dict(os.environ, TEST_ROOT=tmp,
                    PS4PKG_HOME=tmp, NO_COLOR='1'))

    def check(self, commands):
        result = self.run_shell(commands)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rosetta_selects_arm64(self):
        self.check('''
sysctl() { echo 1; }
uname() { echo x86_64; }
test "$(build_arch)" = arm64
''')

    def test_intel_selects_x86_64(self):
        self.check('''
sysctl() { return 1; }
uname() { echo x86_64; }
test "$(build_arch)" = x86_64
''')

    def test_wrong_crypto_archive_is_cleaned_before_rebuild(self):
        self.check('''
do_cryptopp() ''' + SOURCE.split('do_cryptopp() ', 1)[1].split('\nzlib_prefix()', 1)[0].replace('$VENDOR_DIR', '$TEST_ROOT') + '''
BUILD_ARCH=arm64
BUILD_CXX=/usr/bin/clang++
mkdir -p cryptopp
touch cryptopp/libcryptopp.a
has_build_arch() { return 1; }
sysctl() { echo 2; }
make() { printf '%s\\n' "$*" >> "$TEST_ROOT/make.log"; }
do_cryptopp || exit 1
test "$(head -n 1 make.log)" = clean || exit 1
grep -q -- 'CXXFLAGS=-O3 -DNDEBUG -arch arm64' make.log
''')

    def test_matching_crypto_archive_is_reused(self):
        self.check('''
do_cryptopp() ''' + SOURCE.split('do_cryptopp() ', 1)[1].split('\nzlib_prefix()', 1)[0].replace('$VENDOR_DIR', '$TEST_ROOT') + '''
mkdir -p cryptopp
touch cryptopp/libcryptopp.a
has_build_arch() { return 0; }
make() { echo unexpected > "$TEST_ROOT/unexpected"; return 1; }
do_cryptopp || exit 1
test ! -e unexpected
''')

    def test_zlib_architecture_is_checked(self):
        self.check('''
mkdir -p zlib/lib
touch zlib/lib/libz.dylib
brew() { printf '%s' "$TEST_ROOT/zlib"; }
BUILD_ARCH=arm64
xcrun() { printf '%s\\n' "$*" >> "$TEST_ROOT/lipo.log"; return 0; }
test "$(zlib_prefix)" = "$TEST_ROOT/zlib" || exit 1
grep -q -- '-verify_arch arm64' lipo.log || exit 1
xcrun() { return 1; }
if zlib_prefix; then exit 1; fi
''')

    def test_conda_lipo_on_path_is_not_used(self):
        self.check('''
BUILD_ARCH=arm64
mkdir -p conda/bin
printf '#!/bin/sh\\necho wrong-lipo >&2\\nexit 1\\n' > conda/bin/lipo
chmod +x conda/bin/lipo
export PATH="$TEST_ROOT/conda/bin:$PATH"
xcrun() {
  test "$1" = lipo && test "$2" = -verify_arch &&
    test "$3" = arm64 && test "$4" = library.dylib
}
has_build_arch library.dylib
''')

    def test_consecutive_builds_pin_both_architectures(self):
        for arch in ('arm64', 'x86_64'):
            with self.subTest(arch=arch):
                self.check('BUILD_ARCH=' + arch + '''
BUILD_CXX=/usr/bin/clang++
BUILD_ZLIB="$TEST_ROOT/zlib"
has_build_arch() { return 0; }
cmake() {
  printf '%s\\n' "$@" >> "$TEST_ROOT/cmake.log"
  if [ "$1" = --build ]; then touch "$2/pkg_extractor"; fi
}
do_build || exit 1
do_build || exit 1
test "$(grep -c -- "-DCMAKE_OSX_ARCHITECTURES=$BUILD_ARCH" cmake.log)" = 2 || exit 1
test -f "$EXTRACTOR"
''')

    def test_failure_preserves_full_log(self):
        self.check('''
mktemp() { command mktemp "$TEST_ROOT/build-log.XXXXXX"; }
fail_build() { echo first-diagnostic; echo last-diagnostic; return 1; }
if spin_run test fail_build; then exit 1; fi
grep -q first-diagnostic "$TEST_ROOT"/build-log.*
''')


if __name__ == '__main__':
    unittest.main()
