from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
from conan.tools.apple import fix_apple_shared_install_name
import os

required_conan_version = ">=2.0"


class CapstoneConan(ConanFile):
    name = "capstone"
    description = (
        "Capstone disassembly/disassembler framework: Core (Arm, Arm64, BPF, "
        "EVM, M68K, M680X, MOS65xx, Mips, PPC, RISCV, Sparc, SystemZ, "
        "TMS320C64x, Web Assembly, X86, X86_64, XCore) + bindings."
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.capstone-engine.org"
    topics = (
        "reverse-engineering", "disassembler", "security", "framework", "arm", "arm64",
        "x86", "sparc", "powerpc", "mips", "x86-64", "ethereum", "systemz",
        "webassembly", "m68k", "m0s65xx", "m680x", "tms320c64x", "bpf", "riscv",
    )
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_default_alloc": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_default_alloc": True,
    }
    implements = ["auto_shared_fpic"]

    _archs = ["arm", "m68k", "mips", "ppc", "sparc", "sysz", "xcore", "x86", "tms320c64x", "m680x", "evm"]
    options.update({a: [True, False] for a in _archs})
    default_options.update({a: True for a in _archs})

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "5.0":
            tc.cache_variables["CAPSTONE_BUILD_STATIC"] = not self.options.shared
            tc.cache_variables["CAPSTONE_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["CAPSTONE_BUILD_TESTS"] = False
        tc.cache_variables["CAPSTONE_BUILD_CSTOOL"] = False
        tc.cache_variables["CAPSTONE_ARCHITECUTRE_DEFAULT"] = False
        if Version(self.version) < "5.0":
            tc.cache_variables["CAPSTONE_USE_SYS_DYN_MEM"] = self.options.use_default_alloc
        else:
            tc.cache_variables["CAPSTONE_USE_DEFAULT_ALLOC"] = self.options.use_default_alloc
        for a in self._archs:
            tc.cache_variables[f"CAPSTONE_{a.upper()}_SUPPORT"] = self.options.get_safe(a)
        tc.cache_variables["CAPSTONE_BUILD_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        suffix = "_dll" if is_msvc(self) and self.options.shared and Version(self.version) < "5.0" else ""
        self.cpp_info.libs = [f"capstone{suffix}"]
        if self.options.shared:
            self.cpp_info.defines.append("CAPSTONE_SHARED")
