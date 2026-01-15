from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import export_conandata_patches, get, apply_conandata_patches
from conan.tools.scm import Version
import os


class AUIRecipe(ConanFile):
    name = "aui"
    version = "7.1.2"
    license = "MPL-2.0"
    author = "Alex2772 <alex2772sc@gmail.com>"
    url = "https://github.com/aui-framework/aui"
    description = "Declarative UI toolkit for modern C++20"
    topics = ("ui", "gui", "framework", "cpp20", "declarative")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")
        if self.settings.os == "Linux":
            self.tool_requires("pkgconf/2.1.0")

    def requirements(self):
        self.requires("zlib/1.3.1")
        self.requires("fmt/9.1.0")
        self.requires("range-v3/0.12.0")
        self.requires("glm/0.9.9.8")
        self.requires("openssl/3.2.1")
        self.requires("libcurl/8.6.0")
        self.requires("lunasvg/2.3.2")
        self.requires("libwebp/1.3.2")
        self.requires("freetype/2.13.2")
        self.requires("opus/1.4")
        self.requires("soxr/0.1.3")
        self.requires("gtest/1.14.0")
        self.requires("benchmark/1.8.3")

        if self.settings.os == "Linux":
            self.requires("libbacktrace/cci.20240730")
            self.requires("pulseaudio/14.2")
            self.requires("libx11/1.8.7")
            self.requires("fontconfig/2.15.0")
            self.requires("dbus/1.13.18")
            self.requires("gtk/3.24.24")

        if self.settings.os == "Android":
            self.requires("oboe/1.8.0")

        if self.settings.os in ["Windows", "Linux", "Macos"]:
            self.requires("glew/2.2.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 20)

        if (
            self.settings.compiler == "gcc"
            and Version(self.settings.compiler.version) < "10"
        ):
            raise ConanInvalidConfiguration("gcc < 10 is not supported")
        if (
            self.settings.compiler == "clang"
            and Version(self.settings.compiler.version) < "11"
        ):
            raise ConanInvalidConfiguration("clang < 11 is not supported")
        if (
            self.settings.compiler == "msvc"
            and Version(self.settings.compiler.version) < "193"
        ):  # VS 2022
            raise ConanInvalidConfiguration("msvc < 193 is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["AUI_BUILD_EXAMPLES"] = False
        tc.variables["AUI_INSTALL_RUNTIME_DEPENDENCIES"] = False
        tc.variables["AUIB_NO_PRECOMPILED"] = True
        tc.variables["AUIB_DISABLE"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["aui_audio"].libs = ["aui.audio"]
        self.cpp_info.components["aui_audio"].includedirs = ["include"]
        self.cpp_info.components["aui_audio"].requires = ["opus::opus", "soxr::soxr"]
        if self.settings.os == "Linux":
            self.cpp_info.components["aui_audio"].requires.append(
                "pulseaudio::pulseaudio"
            )
        elif self.settings.os == "Android":
            self.cpp_info.components["aui_audio"].requires.append("oboe::oboe")
        elif self.settings.os == "Windows":
            self.cpp_info.components["aui_audio"].system_libs = [
                "winmm",
                "dsound",
                "dxguid",
            ]
        elif self.settings.os in ["Macos", "iOS"]:
            self.cpp_info.components["aui_audio"].frameworks = [
                "CoreAudio",
                "AVFoundation",
                "AudioToolbox",
            ]
            if self.settings.os == "Macos":
                self.cpp_info.components["aui_audio"].frameworks.extend(
                    ["AppKit", "Cocoa", "CoreData", "Foundation", "QuartzCore"]
                )

        self.cpp_info.components["aui_core"].libs = ["aui.core"]
        self.cpp_info.components["aui_core"].includedirs = ["include"]
        self.cpp_info.components["aui_core"].requires = [
            "fmt::fmt",
            "range-v3::range-v3",
            "glm::glm",
        ]
        if self.settings.os == "Linux":
            self.cpp_info.components["aui_core"].requires.append(
                "libbacktrace::libbacktrace"
            )
            self.cpp_info.components["aui_core"].system_libs = ["pthread", "dl"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["aui_core"].system_libs = [
                "dbghelp",
                "shell32",
                "shlwapi",
                "kernel32",
                "psapi",
            ]
        elif self.settings.os == "Android":
            self.cpp_info.components["aui_core"].system_libs = ["log"]

        self.cpp_info.components["aui_crypt"].libs = ["aui.crypt"]
        self.cpp_info.components["aui_crypt"].includedirs = ["include"]
        self.cpp_info.components["aui_crypt"].requires = ["openssl::openssl"]
        if self.settings.os == "Windows":
            self.cpp_info.components["aui_crypt"].system_libs = ["wsock32", "ws2_32"]

        self.cpp_info.components["aui_curl"].libs = ["aui.curl"]
        self.cpp_info.components["aui_curl"].includedirs = ["include"]
        self.cpp_info.components["aui_curl"].requires = ["libcurl::libcurl"]

        self.cpp_info.components["aui_image"].libs = ["aui.image"]
        self.cpp_info.components["aui_image"].includedirs = ["include"]
        self.cpp_info.components["aui_image"].requires = [
            "lunasvg::lunasvg",
            "libwebp::libwebp",
        ]

        self.cpp_info.components["aui_json"].libs = ["aui.json"]
        self.cpp_info.components["aui_json"].includedirs = ["include"]

        self.cpp_info.components["aui_network"].libs = ["aui.network"]
        self.cpp_info.components["aui_network"].includedirs = ["include"]
        if self.settings.os == "Windows":
            self.cpp_info.components["aui_network"].system_libs = [
                "wsock32",
                "ws2_32",
                "iphlpapi",
            ]

        self.cpp_info.components["aui_toolbox"].includedirs = ["include"]

        self.cpp_info.components["aui_uitests"].libs = ["aui.uitests"]
        self.cpp_info.components["aui_uitests"].includedirs = ["include"]
        self.cpp_info.components["aui_uitests"].requires = [
            "gtest::gtest",
            "benchmark::benchmark",
        ]

        self.cpp_info.components["aui_views"].libs = ["aui.views"]
        self.cpp_info.components["aui_views"].includedirs = ["include"]
        self.cpp_info.components["aui_views"].requires = ["freetype::freetype"]
        if self.settings.os in ["Windows", "Linux", "Macos"]:
            self.cpp_info.components["aui_views"].requires.append("glew::glew")

        if self.settings.os == "Linux":
            self.cpp_info.components["aui_views"].requires.extend(
                ["libx11::libx11", "dbus::dbus", "fontconfig::fontconfig", "gtk::gtk"]
            )
        elif self.settings.os == "Windows":
            self.cpp_info.components["aui_views"].system_libs = [
                "dwmapi",
                "winmm",
                "shlwapi",
                "gdi32",
                "ole32",
                "opengl32",
                "uuid"
            ]
        elif self.settings.os == "Android":
            self.cpp_info.components["aui_views"].system_libs = [
                "EGL",
                "GLESv2",
                "GLESv3",
            ]
        elif self.settings.os == "iOS":
            self.cpp_info.components["aui_views"].frameworks = ["OpenGLES"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["aui_views"].frameworks = [
                "AppKit",
                "Cocoa",
                "CoreData",
                "Foundation",
                "QuartzCore",
                "UniformTypeIdentifiers",
                "OpenGL",
            ]

        self.cpp_info.components["aui_xml"].libs = ["aui.xml"]
        self.cpp_info.components["aui_xml"].includedirs = ["include"]

        # Defines
        if not self.options.shared:
            self.cpp_info.defines.append("AUI_STATIC")

        if self.settings.build_type == "Debug":
            self.cpp_info.defines.append("AUI_DEBUG=1")
        else:
            self.cpp_info.defines.append("AUI_DEBUG=0")

        self.cpp_info.defines.extend(
            [
                "API_AUI_AUDIO=AUI_IMPORT",
                "API_AUI_CORE=AUI_IMPORT",
                "API_AUI_CRYPT=AUI_IMPORT",
                "API_AUI_CURL=AUI_IMPORT",
                "API_AUI_DATA=AUI_IMPORT",
                "API_AUI_IMAGE=AUI_IMPORT",
                "API_AUI_JSON=AUI_IMPORT",
                "API_AUI_NETWORK=AUI_IMPORT",
                "API_AUI_UITESTS=AUI_IMPORT",
                "API_AUI_UPDATER=AUI_IMPORT",
                "API_AUI_VIEWS=AUI_IMPORT",
                "API_AUI_XML=AUI_IMPORT",
                "GLM_ENABLE_EXPERIMENTAL=1",
            ]
        )

        # Platform defines
        if self.settings.os == "Windows":
            self.cpp_info.defines.append("AUI_PLATFORM_WIN=1")
        elif self.settings.os == "Linux":
            self.cpp_info.defines.extend(
                ["AUI_PLATFORM_LINUX=1", "AUI_PLATFORM_UNIX=1"]
            )
        elif self.settings.os == "Macos":
            self.cpp_info.defines.extend(
                ["AUI_PLATFORM_APPLE=1", "AUI_PLATFORM_MACOS=1", "AUI_PLATFORM_UNIX=1"]
            )
        elif self.settings.os == "Android":
            self.cpp_info.defines.extend(
                ["AUI_PLATFORM_ANDROID=1", "AUI_PLATFORM_UNIX=1"]
            )
        elif self.settings.os == "iOS":
            self.cpp_info.defines.extend(
                ["AUI_PLATFORM_APPLE=1", "AUI_PLATFORM_IOS=1", "AUI_PLATFORM_UNIX=1"]
            )
        elif self.settings.os == "Emscripten":
            self.cpp_info.defines.append("AUI_PLATFORM_EMSCRIPTEN=1")

        # Compiler defines
        if self.settings.compiler in ["clang", "apple-clang"]:
            self.cpp_info.defines.append("AUI_COMPILER_CLANG=1")
        elif self.settings.compiler == "gcc":
            self.cpp_info.defines.append("AUI_COMPILER_GCC=1")
        elif self.settings.compiler == "msvc":
            self.cpp_info.defines.append("AUI_COMPILER_MSVC=1")

        # Arch defines
        if "arm" in str(self.settings.arch):
            if "64" in str(self.settings.arch):
                self.cpp_info.defines.append("AUI_ARCH_ARM_64=1")
            else:
                self.cpp_info.defines.append("AUI_ARCH_ARM_V7=1")
        else:
            if "64" in str(self.settings.arch):
                self.cpp_info.defines.append("AUI_ARCH_X86_64=1")
            else:
                self.cpp_info.defines.append("AUI_ARCH_X86=1")
