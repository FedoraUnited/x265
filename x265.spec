%global gitdate 20170226
%global commit0 3daed96a7d8f409c8e30e1226122ab4935561173
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver .%{gitdate}git%{shortcommit0}


Summary: 	H.265/HEVC encoder
Name: 		x265
Group:		Applications/Multimedia
Version: 	2.2
Release: 	2%{?gver}%{?dist}
URL: 		http://x265.org/
Source0:	https://github.com/videolan/x265/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
Source1: 	%{name}-snapshot.sh
License: 	GPLv2+ and BSD
BuildRequires: 	cmake
BuildRequires: 	yasm
BuildRequires: 	git

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
%autosetup -n x265-%{commit0} 

%ifarch x86_64
sed -i 's|set(LIB_INSTALL_DIR lib CACHE STRING "Install location of libraries")|set(LIB_INSTALL_DIR lib64 CACHE STRING "Install location of libraries")|g' source/CMakeLists.txt
%endif

mkdir -p build-8 build-10 build-12


%build

%ifarch x86_64
pushd build-12
    cmake ../source \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DHIGH_BIT_DEPTH='TRUE' \
      -DMAIN12='TRUE' \
      -DEXPORT_C_API='FALSE' \
      -DENABLE_CLI='FALSE' \
      -DENABLE_SHARED='FALSE'
    make
popd

    pushd build-10
    cmake ../source \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DHIGH_BIT_DEPTH='TRUE' \
      -DEXPORT_C_API='FALSE' \
      -DENABLE_CLI='FALSE' \
      -DENABLE_SHARED='FALSE'
    make
popd

    pushd build-8
    ln -s ../build-10/libx265.a libx265_main10.a
    ln -s ../build-12/libx265.a libx265_main12.a

    cmake ../source \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DENABLE_SHARED='TRUE' \
      -DEXTRA_LIB='x265_main10.a;x265_main12.a' \
      -DEXTRA_LINK_FLAGS='-L.' \
      -DLINKED_10BIT='TRUE' \
      -DLINKED_12BIT='TRUE'
    make
popd

%else

    pushd build-8

    cmake ../source \
      -DCMAKE_INSTALL_PREFIX='/usr' \
      -DENABLE_SHARED='TRUE'

%endif

%install

pushd build-8
make DESTDIR=%{buildroot} install
rm %{buildroot}%{_libdir}/libx265.a
install -Dpm644 %{_builddir}/%{name}-%{commit0}/COPYING %{buildroot}%{_pkgdocdir}/COPYING

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%{_bindir}/x265

%files libs
%dir %{_pkgdocdir}
%{_pkgdocdir}/COPYING
%{_libdir}/libx265.so.*

%files devel
%doc doc/*
%{_includedir}/x265.h
%{_includedir}/x265_config.h
%{_libdir}/libx265.so
%{_libdir}/pkgconfig/x265.pc

%changelog

* Sun Feb 26 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 2.2-2-20170226git3daed96
- Updated to 2.2-2-20170226git3daed96

* Fri Jul 08 2016 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.9-2-20160221git40ba1eb
- Massive rebuild

* Tue Jul 14 2015 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.9-1-20160221git40ba1eb
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
