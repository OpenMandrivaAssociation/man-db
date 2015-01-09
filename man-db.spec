# We need to allow undefined symbols - libmandb relies on them
%define _disable_ld_no_undefined 1
%global cache /var/cache/man

Summary:	A set of documentation tools: man, apropos and whatis
Name:		man-db
Version:	2.7.1
Release:	2
License:	GPLv2
Group:		System/Base
Url:		http://www.nongnu.org/man-db/
Source0:	http://download.savannah.gnu.org/releases/man-db/%{name}-%{version}.tar.xz
Source1:	man-db.crondaily
Source2:	man-db.sysconfig
Patch0:		man-db-2.6.3-recompress-xz.patch
BuildRequires:	groff
BuildRequires:	xz
BuildRequires:	gdbm-devel
BuildRequires:	lzma-devel
BuildRequires:	pkgconfig(libpipeline)
BuildRequires:	pkgconfig(systemd)
Requires(post):	rpm-helper
Requires:	groff-base
Requires:	xz
%rename	man

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
%setup -q

%apply_patches
# Needed after patch0
autoconf

%build
%configure \
	--with-sections="1 1p 8 2 3 3p 4 5 6 7 9 0p n l p o 1x 2x 3x 4x 5x 6x 7x 8x" \
	--disable-setuid \
	--enable-threads=posix

%make CC="%{__cc} %{optflags}" V=1
chmod 0755 ./src/man

%install
%makeinstall_std prefix=%{_prefix} INSTALL='%{__install} -p'

# install cron script for man-db creation/update
install -m755 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/cron.daily/man-db.cron

# move the documentation to relevant place
mv %{buildroot}%{_datadir}/doc/man-db/* ./

# remove zsoelim - part of groff package
rm %{buildroot}%{_libexecdir}/%{name}/zsoelim
rm %{buildroot}%{_datadir}/man/man1/zsoelim.1*

# install cache directory
install -d -m 0755 %{buildroot}%{cache}

# fix tmpfile conf
sed -i -e "s/man root/root man/g" init/systemd/man-db.conf

# config for cron script
install -D -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/man-db
install -D -p -m 0644 init/systemd/man-db.conf %{buildroot}%{_tmpfilesdir}/man-db.conf

%find_lang %{name}
%find_lang %{name}-gnulib

%post
%tmpfiles_create man-db.conf

%files -f %{name}.lang,%{name}-gnulib.lang
%doc README man-db-manual.txt man-db-manual.ps docs/COPYING ChangeLog NEWS
%config(noreplace) %{_sysconfdir}/man_db.conf
%config(noreplace) %{_sysconfdir}/sysconfig/man-db
%config(noreplace) %{_tmpfilesdir}/man-db.conf
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
%{_libexecdir}/man-db/globbing
%{_libexecdir}/man-db/manconv
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
%lang(es) %{_mandir}/es/*/*
%lang(it) %{_mandir}/it/*/*
%attr(0755,root,root) %dir %{cache}
