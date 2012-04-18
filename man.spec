%global cache /var/cache/man

Summary:	A set of documentation tools: man, apropos and whatis
Name:		man
Version:	2.6.1
Release:	1
License:	GPLv2
Group:		System/Base
Url:		http://www.nongnu.org/man-db/
Source0:	http://download.savannah.gnu.org/releases/man-db/%{name}-db-%{version}.tar.gz
Source1:	man-db.crondaily
Source2:	man-db.sysconfig
Patch0:		man-db-2.6.1-recompress-xz.patch
Requires:	groff-for-man
Requires:	xz
BuildRequires:	xz, lzma-devel, gdbm-devel, groff-for-man, pkgconfig(libpipeline)

# We need to allow undefined symbols - libmandb relies on them
%define _disable_ld_no_undefined 1

%description
The man package includes three tools for finding information and/or
documentation about your Linux system: man, apropos and whatis. The man
system formats and displays on-line manual pages about commands or
functions on your system. Apropos searches the whatis database
(containing short descriptions of system commands) for a string. Whatis
searches its own database for a complete word.

The man package should be installed on your system because it is the
primary way for find documentation on a Mandriva Linux system.

%prep
%setup -q -n %name-db-%version
%patch0 -p1 -b .recompress~
# Needed after patch0
autoconf
%configure \
	--with-sections="1 1p 8 2 3 3p 4 5 6 7 9 0p n l p o 1x 2x 3x 4x 5x 6x 7x 8x" \
	--disable-setuid \
	--enable-threads=posix

%build
%make CC="%__cc %optflags" V=1
chmod 0755 ./src/man

%install
%makeinstall_std prefix=%_prefix INSTALL='%__install -p'

# install cron script for man-db creation/update
%__install -m755 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/cron.daily/man-db.cron

# move the documentation to relevant place
mv $RPM_BUILD_ROOT%{_datadir}/doc/man-db/* ./

# remove zsoelim - part of groff package
rm $RPM_BUILD_ROOT%{_bindir}/zsoelim
rm $RPM_BUILD_ROOT%{_datadir}/man/man1/zsoelim.1

# install cache directory
%__install -d -m 0755  $RPM_BUILD_ROOT%{cache}

# config for cron script
%__install -D -p -m 0644 %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/man-db

%find_lang %{name}-db
%find_lang %{name}-db-gnulib

%clean
rm -rf %{buildroot}

%files -f %{name}-db.lang,%{name}-db-gnulib.lang
%defattr(-,root,root)
%doc README man-db-manual.txt man-db-manual.ps docs/COPYING ChangeLog NEWS
%config(noreplace) %{_sysconfdir}/man_db.conf
%config(noreplace) %{_sysconfdir}/sysconfig/man-db
%{_sysconfdir}/cron.daily/man-db.cron
%{_sbindir}/accessdb
%{_bindir}/man
%{_bindir}/whatis
%{_bindir}/apropos
%{_bindir}/manpath
%{_bindir}/lexgrog
%{_bindir}/catman
%{_bindir}/mandb
%dir %{_libdir}/man-db
%{_libdir}/man-db/globbing
%{_libdir}/man-db/manconv
%{_libdir}/man-db/*.so*
# documentation and translation
%{_mandir}/man1/apropos.1*
%{_mandir}/man1/lexgrog.1*
%{_mandir}/man1/man.1*
%{_mandir}/man1/manconv.1*
%{_mandir}/man1/manpath.1*
%{_mandir}/man1/whatis.1*
%{_mandir}/man5/manpath.5*
%{_mandir}/man8/accessdb.8*
%{_mandir}/man8/catman.8*
%{_mandir}/man8/mandb.8*
%lang(es) %_mandir/es/*/*
%lang(it) %_mandir/it/*/*
%attr(0755,root,root)   %dir %{cache}
