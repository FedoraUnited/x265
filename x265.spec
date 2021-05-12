%global commit0 f0c1022b6be121a753ff02853fbe33da71988656
%global shortcommit0 %(c=%{commit0}; echo ${c:0:12})  
%global gver .git%{shortcommit0}

%global debug_package %{nil}
%global api_version 199

Summary: 	H.265/HEVC encoder
Name: 		x265
Group:		Applications/Multimedia
Version: 	3.5
Release: 	7%{?dist}
URL: 		http://x265.org/
Source0:	https://bitbucket.org/multicoreware/x265_git/downloads/x265_%{version}.tar.gz
Patch:		pkgconfig_fix.patch
# fix building as PIC
Patch1:		%{name}-pic.patch
Patch2:		%{name}-high-bit-depth-soname.patch
Patch3:		%{name}-detect_cpu_armhfp.patch
Patch4:		%{name}-arm-cflags.patch
License: 	GPLv2+ and BSD
BuildRequires:	cmake3
BuildRequires:	nasm
BuildRequires:	gcc-c++
BuildRequires:  numactl-devel
BuildRequires:	ninja-build

%description
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the
highest performance on a wide variety of hardware platforms.

This package contains the command line encoder.

%package libs
Summary: H.265/HEVC encoder library
Group: Development/Libraries

%description libs
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the
highest performance on a wide variety of hardware platforms.

This package contains the shared library.

%package devel
Summary: H.265/HEVC encoder library development files
Group: Development/Libraries
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
The primary objective of x265 is to become the best H.265/HEVC encoder
available anywhere, offering the highest compression efficiency and the
highest performance on a wide variety of hardware platforms.

This package contains the shared library development files.

%prep
%autosetup -n %{name}_%{version} -p1

%ifarch x86_64
sed -i 's|set(LIB_INSTALL_DIR lib CACHE STRING "Install location of libraries")|set(LIB_INSTALL_DIR lib64 CACHE STRING "Install location of libraries")|g' source/CMakeLists.txt
%endif

mkdir -p build-8 build-10 build-12


%build

%ifarch x86_64
pushd build-12
mkdir -p build
    %cmake  -B build \
      -S %{_builddir}/%{name}_%{version}/source \
      -G Ninja \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
      -DHIGH_BIT_DEPTH='TRUE' \
      -DMAIN12='TRUE' \
      -DEXPORT_C_API='FALSE' \
      -DENABLE_CLI='FALSE' \
      -DENABLE_SHARED='TRUE' \
      -Wno-dev 
      
    %ninja_build -C build
popd

    pushd build-10
    mkdir -p build
    %cmake -B build \
      -S %{_builddir}/%{name}_%{version}/source \
      -G Ninja \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
      -DHIGH_BIT_DEPTH='TRUE' \
      -DEXPORT_C_API='FALSE' \
      -DENABLE_CLI='FALSE' \
      -DENABLE_SHARED='TRUE' \
      -Wno-dev 
    %ninja_build -C build -j2
popd

    pushd build-8
    mkdir -p build
    %cmake -B build \
    -S %{_builddir}/%{name}_%{version}/source \
    -G Ninja \
    -DCMAKE_INSTALL_PREFIX='/usr' \
    -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DCMAKE_SKIP_RPATH=YES \
    -DENABLE_PIC=ON \
    -DENABLE_SHARED=ON \
    -DENABLE_HDR10_PLUS='TRUE' \
    -DGIT_ARCHETYPE="1" \
    -DENABLE_ASSEMBLY=ON \
    -Wno-dev 

    %ninja_build -C build -j2
popd

%else

    pushd build-8
    mkdir -p build
    %cmake  -B build \
      -S %{_builddir}/%{name}_%{version}/source \
      -G Ninja \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
      -DENABLE_SHARED='TRUE' \
      -DENABLE_HDR10_PLUS='TRUE' \
      -Wno-dev
      
    %ninja_build -C build -j2
    popd
%endif

%install
pushd build-8
  %ninja_install -C build
  cp -n $PWD/build/libx265.so* %{buildroot}%{_libdir}/
popd

install -m 0755 -p \
  build-12/build/libx265_main12.so.%{api_version} \
  build-10/build/libx265_main10.so.%{api_version} \
  %{buildroot}%{_libdir}


if [ ! -f %{buildroot}/%{_bindir}/x265 ]; then
mkdir -p %{buildroot}/%{_bindir} && cp -f build-8/build/x265 %{buildroot}/%{_bindir}/
fi

# maybe we need a static in the future
find %{buildroot} -name "*.a" -delete


%ldconfig_scriptlets libs

%files
%{_bindir}/x265

%files libs
%license COPYING
%{_libdir}/libhdr10plus.so
%{_libdir}/lib%{name}.so.%{api_version}
%ifarch x86_64 aarch64
%{_libdir}/lib%{name}_main10.so.%{api_version}
%{_libdir}/lib%{name}_main12.so.%{api_version}
%endif

%files devel
%doc doc/*
%{_includedir}/hdr10plus.h
%{_includedir}/%{name}.h
%{_includedir}/%{name}_config.h
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog

* Sat May 08 2021 David Va <davidva AT tuta DOT io> - 3.5-7
- Updated to 3.5

* Fri Jan 29 2021 David Va <davidva AT tuta DOT io> - 3.4-8
- Updated to current commit stable

* Sat May 30 2020 David Va <davidva AT tuta DOT io> - 3.4-7
- Updated to 3.4

* Tue Feb 18 2020 David Va <davidva AT tuta DOT io> - 3.3-7
- Updated to 3.3-7

* Sun Dec 01 2019 David Va <davidva AT tuta DOT io> - 3.2.1-7
- Updated to 3.2.1-7

* Fri Aug 02 2019 David Vásquez <davidjeremias82 AT gmail DOT com> - 3.1.2-7
- Updated to 3.1.2-7

* Thu Jul 11 2019 David Vásquez <davidjeremias82 AT gmail DOT com> - 3.1.1-7
- Updated to 3.1.1-7

* Fri Jun 21 2019 David Vásquez <davidjeremias82 AT gmail DOT com> - 3.1-7.git492e3c4
- Updated to 3.1-7.git492e3c4

* Wed Feb 06 2019 David Vásquez <davidjeremias82 AT gmail DOT com> - 3.0-7.git9394080
- Updated to 3.0-7.git9394080

* Wed Oct 10 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.9-7.git975a2e1
- Updated to 2.9-7.git975a2e1

* Tue May 22 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.8-3.gitba0d009
- Updated to 2.8-3.gitba0d009

* Sun Apr 15 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.7-3.git56b216f
- Devel package fix

* Wed Feb 21 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.7-2.git56b216f
- Updated to 2.7-2.git56b216f

* Sat Dec 02 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.6-2.gite293b13
- Updated to 2.6-2.gite293b13

* Mon Oct 02 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.5-3.gitb28e239
- Updated to 2.5-3.gitb28e239

* Tue Sep 26 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.5-2.gite8a6c75
- Updated to 2.5-2.gite8a6c75

* Thu May 25 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.4-2.gitb2d3ae4
- Updated to 2.4-2.gitb2d3ae4

* Mon Apr 17 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.3-2.git97492ac
- Updated to 2.3-2-20170417git97492ac

* Sun Feb 26 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.2-2.git3daed96
- Updated to 2.2-2-20170226git3daed96

* Fri Jul 08 2016 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.9-2.git40ba1eb
- Massive rebuild

* Tue Jul 14 2015 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.9-1.git40ba1eb
- Updated to 1.9-20160221-40ba1eb

* Tue Jul 14 2015 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.7-1
- Updated to 1.7
- Patched detection of ARM
- Added git tag in x265-snapshot.sh
- Thanks to Torsten Gruner and aloisio@gmx.com for tips in build (ARM patches)

* Wed Apr 15 2015 Dominik Mierzejewski <rpm@greysector.net> 1.6-1
- update to 1.6 (ABI bump, rfbz#3593)
- release tarballs are now hosted on videolan.org
- drop obsolete patches

* Thu Dec 18 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-6
- fix build on armv7l arch (partially fix rfbz#3361, patch by Nicolas Chauvet)
- don't run tests on ARM for now (rfbz#3361)

* Sun Aug 17 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-5
- don't include contributor agreement in doc
- make sure /usr/share/doc/x265 is owned
- add a comment noting which files are BSD-licenced

* Fri Aug 08 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-4
- don't create bogus soname (patch by Xavier)

* Thu Jul 17 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-3
- fix tr call to remove DOS EOL
- build the library with -fPIC on arm and i686, too

* Sun Jul 13 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-2
- use version in source URL
- update License tag
- fix EOL in drag-uncrustify.bat
- don't link test binaries with shared binary on x86 (segfault)

* Thu Jul 10 2014 Dominik Mierzejewski <rpm@greysector.net> 1.2-1
- initial build
- fix pkgconfig file install location
- link test binaries with shared library
