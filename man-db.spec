# We need to allow undefined symbols - libmandb relies on them
%define _disable_ld_no_undefined 1
%global cache /var/cache/man
%ifnarch %{riscv}
%global optflags %{optflags} --rtlib=compiler-rt
%endif

Summary:	A set of documentation tools: man, apropos and whatis
Name:		man-db
Version:	2.11.1
Release:	1
License:	GPLv2
Group:		System/Base
Url:		http://www.nongnu.org/man-db/
Source0:	http://download.savannah.gnu.org/releases/man-db/%{name}-%{version}.tar.xz
Source1:	man-db.timer
Source2:	man-db.service
Source3:	man-db.sysusers
Patch1:		man-db-2.10.0-clang.patch
Patch2:		man-db-2.8.3-change-owner-of-man-cache.patch
BuildRequires:	groff
BuildRequires:	flex
BuildRequires:	xz
BuildRequires:	zstd
BuildRequires:	gdbm-devel
BuildRequires:	po4a
BuildRequires:	pkgconfig(libpipeline)
BuildRequires:	pkgconfig(zlib)
# For macros.systemd (_tmpfilesdir, _presetdir, _unitdir)
BuildRequires:	systemd-rpm-macros
BuildRequires:	pkgconfig(libseccomp)
# The configure script checks for the best available pager at build time,
# let's prevent it from picking "more"
BuildRequires:	less
Requires(pre):	systemd
Requires:	groff-base
Requires:	less
Recommends:	zstd
%systemd_requires
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
%autosetup -p1
# Needed after patches 0 and 3
autoheader
autoconf

%build
%configure \
	--with-sections="1 1p 8 2 3 3p 4 5 6 7 9 0p n l p o 1x 2x 3x 4x 5x 6x 7x 8x" \
	--with-compress=zstd \
	--disable-setuid \
	--enable-threads=posix \
	--with-pager="less -X" \
	--disable-cache-owner \
	--with-lzip=lzip \
	--with-override-dir=overrides \
	--with-systemdsystemunitdir=%{_unitdir} \
	--with-systemdtmpfilesdir=%{_tmpfilesdir} \
	--with-libseccomp

%make_build CC="%{__cc} %{optflags}" V=1
chmod 0755 ./src/man

%install
%make_install prefix=%{_prefix} INSTALL='%{__install} -p'

# move the documentation to relevant place
mv %{buildroot}%{_datadir}/doc/man-db/* ./

# remove zsoelim - part of groff package
rm %{buildroot}%{_libexecdir}/%{name}/zsoelim
rm %{buildroot}%{_datadir}/man/man1/zsoelim.1*

# install cache directory
install -d -m 0755 %{buildroot}%{cache}

# fix tmpfile conf
sed -i -e "s/man root/root man/g" init/systemd/man-db.conf

install -D -m644 %{SOURCE1} %{buildroot}%{_unitdir}/man-db.timer
install -D -m644 %{SOURCE2} %{buildroot}%{_unitdir}/man-db.service
install -Dpm 644 %{SOURCE3} %{buildroot}%{_sysusersdir}/%{name}.conf

cat >%{buildroot}%{_sbindir}/update-man-cache <<'EOF'
#!/bin/sh
# Just in case /var/cache is tmpfs or similar
if ! [ -d %{cache} ]; then
    mkdir -p -m 0755 %{cache}
    chown man:man %{cache}
fi
exec %{_bindir}/mandb --quiet
EOF
chmod 0755 %{buildroot}%{_sbindir}/update-man-cache
install -D -p -m 0644 init/systemd/man-db.conf %{buildroot}%{_tmpfilesdir}/man-db.conf

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-man-db.preset << EOF
enable man-db.timer
EOF

%find_lang %{name} --with-man --all-name

%pre
%sysusers_create_package man-db.conf %{SOURCE3}

%post
%systemd_post %{name}.timer

%preun
%systemd_preun %{name}.timer

%files -f %{name}.lang
%doc man-db-manual.txt man-db-manual.ps ChangeLog
%config(noreplace) %{_sysconfdir}/man_db.conf
%config(noreplace) %{_tmpfilesdir}/man-db.conf
%{_sysusersdir}/%{name}.conf
%{_presetdir}/86-man-db.preset
%{_sbindir}/accessdb
%{_bindir}/man
%{_bindir}/whatis
%{_bindir}/apropos
%{_bindir}/manpath
%{_bindir}/lexgrog
%{_bindir}/man-recode
%{_bindir}/catman
%{_bindir}/mandb
%{_sbindir}/update-man-cache
%dir %{_libdir}/man-db
%{_libexecdir}/man-db/globbing
%{_libexecdir}/man-db/manconv
%{_libdir}/man-db/*.so*
%{_unitdir}/man-db.timer
%{_unitdir}/man-db.service
# documentation and translation
%doc %{_mandir}/man1/apropos.1*
%doc %{_mandir}/man1/lexgrog.1*
%doc %{_mandir}/man1/man.1*
%doc %{_mandir}/man1/man-recode.1*
%doc %{_mandir}/man1/manconv.1*
%doc %{_mandir}/man1/manpath.1*
%doc %{_mandir}/man1/whatis.1*
%doc %{_mandir}/man5/manpath.5*
%doc %{_mandir}/man8/accessdb.8*
%doc %{_mandir}/man8/catman.8*
%doc %{_mandir}/man8/mandb.8*
%attr(0755,man,man) %dir %{cache}
