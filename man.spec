Summary:	A set of documentation tools: man, apropos and whatis
Name:		man
Version:	1.6g
Release:	%mkrel 1
License:	GPLv2
Group:		System/Base
Url:		http://primates.ximian.com/~flucifredi/man/
Source0:	http://primates.ximian.com/~flucifredi/man/%{name}-%{version}.tar.gz
Source1:	makewhatis.cronweekly
Source2:	makewhatis.crondaily

# Japanese patches
Patch0:		man-1.5h1-gencat.patch
Patch1:		man-1.5g-nonrootbuild.patch
Patch2:		man-1.5j-i18n.patch

Patch10:	man-1.5k-confpath.patch
Patch11:	man-1.5h1-make.patch
Patch12:	man-1.5k-nonascii.patch
Patch13:	man-1.6e-security.patch
Patch14:	man-1.6e-mandirs.patch
Patch15:	man-1.5m2-bug11621.patch
Patch16:	man-1.5k-sofix.patch
Patch17:	man-1.5m2-buildroot.patch
Patch18:	man-1.5i2-newline.patch
Patch19:	man-1.5j-utf8.patch
Patch20:	man-1.5i2-overflow.patch
Patch21:	man-1.5j-nocache.patch
Patch22:	man-1.6e-use_i18n_vars_in_a_std_way.patch
Patch23:	man-1.5m2-no-color-for-printing.patch
# ignore SIGPIPE signals, so no error messages are displayed
# when the pipe is broken before the formatting of the man page
# (which may take some time) is finished.
# the typical case is "man foo | head -1"
Patch24:	man-1.5m2-sigpipe.patch
# avoid adding a manpage already in the list
Patch26:	man-1.5m2-multiple.patch
# i18n fixes for whatis and makewhatis
Patch27:	man-1.6e-new_sections.patch




Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires:	groff-for-man
Requires:	xz
BuildRequires:	xz

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
%patch0 -p0 -b .jp2~
%patch1 -p1 -b .nonrootbuild~
%patch2 -p1 -b .i18n~

%patch10 -p0 -b .confpath~
%patch11 -p1 -b .make~
%patch12 -p1 -b .nonascii~
%patch13 -p1 -b .security~
%patch14 -p1 -b .mandirs~
%patch15 -p1 -b .ad~
%patch16 -p1 -b .sofix~
%patch17 -p1 -b .less~
%patch18 -p0 -b .newline~
%patch19 -p1 -b .utf8~
%patch20 -p1 -b .overflow~
%patch21 -p1 -b .nocache~
%patch22 -p1 -b .use_i18n_vars_in_a_std_way~
%patch23 -p1 -b .color~
%patch24 -p1 -b .sigpipe~
%patch26 -p1 -b .multiple~
%patch27 -p1 -b .new_sections~

for i in $(find man -name man.conf.man); do
	mv $i ${i%man.conf.man}man.config.man
done
for i in $(find man -name man.conf.5); do
	mv $i ${i%man.conf.5}man.config.5
done

for src in msgs/mess.[a-z][a-z]; do
	charset=$(sed 's/^.*codeset=//' ${src}.codeset)
	iconv -t utf-8 -f ${charset} -o ${src}.utf ${src} && mv ${src}.utf ${src}
	echo '$ codeset=utf-8' > ${src}.codeset
done

%build
./configure -default -confdir %{_sysconfdir} +sgid +fhs +lang all 
#	-compatibility_mode_for_colored_groff
%make CFLAGS="%{optflags}" LDFLAGS="%{ldflags}"

%install
rm -rf %{buildroot}
%makeinstall_std

install -m755 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/cron.weekly/makewhatis.cron
install -m755 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/cron.daily/makewhatis.cron

for i in 1 2 3 4 5 6 7 8 9 n; do
	mkdir -p %{buildroot}/var/cache/man/cat$i
	mkdir -p %{buildroot}/var/cache/man/local/cat$i
	mkdir -p %{buildroot}/var/cache/man/X11R6/cat$i
done

# symlinks for manpath
pushd %{buildroot}
  ln -s man .%{_bindir}/manpath
  ln -s man.1%{_extension} .%{_mandir}/man1/manpath.1%{_extension}
popd

# those are provided in the man-pages-xx packages
rm -rf %{buildroot}%{_mandir}/{de,fr,it,pl}

# Fix makewhatis perms
chmod 755 %{buildroot}%{_sbindir}/makewhatis

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_sysconfdir}/cron.weekly/makewhatis.cron
%{_sysconfdir}/cron.daily/makewhatis.cron
%attr(2755,root,man) %{_bindir}/man
%{_bindir}/manpath
%{_bindir}/apropos
%{_bindir}/whatis
%{_bindir}/man2dvi
%{_sbindir}/makewhatis
%config(noreplace) %{_sysconfdir}/man.config
%{_mandir}/man8/*
%{_mandir}/man5/*
%{_mandir}/man1/*
# translated man pages
%lang(bg) %{_mandir}/bg/man?/*
%lang(cs) %{_mandir}/cs/man?/*
%lang(da) %{_mandir}/da/man?/*
%lang(el) %{_mandir}/el/man?/*
%lang(es) %{_mandir}/es/man?/*
%lang(fi) %{_mandir}/fi/man?/*
%lang(hr) %{_mandir}/hr/man?/*
%lang(ja) %{_mandir}/ja/man?/*
%lang(ko) %{_mandir}/ko/man?/*
%lang(nl) %{_mandir}/nl/man?/*
%lang(pt) %{_mandir}/pt/man?/*
%lang(ro) %{_mandir}/ro/man?/*
%lang(sl) %{_mandir}/sl/man?/*
%{_bindir}/man2html

%attr(0775,root,man) %dir /var/cache/man/cat[123456789n]
%attr(0775,root,man) %dir /var/cache/man/local
%attr(0775,root,man) %dir /var/cache/man/local/cat[123456789n]
%attr(0775,root,man) %dir /var/cache/man/X11R6
%attr(0775,root,man) %dir /var/cache/man/X11R6/cat[123456789n]

# translation of man program. It doesn't use gettext format, so
# find_lang doesn't find them... manual setting is needed
%lang(bg) %{_datadir}/locale/bg/man
%lang(cs) %{_datadir}/locale/cs/man
%lang(da) %{_datadir}/locale/da/man
%lang(de) %{_datadir}/locale/de/man
%lang(el) %{_datadir}/locale/el/man
%lang(en) %{_datadir}/locale/en/man
%lang(es) %{_datadir}/locale/es/man
%lang(fi) %{_datadir}/locale/fi/man
%lang(fr) %{_datadir}/locale/fr/man
%lang(hr) %{_datadir}/locale/hr/man
%lang(it) %{_datadir}/locale/it/man
%lang(ja) %{_datadir}/locale/ja/man
%lang(ko) %{_datadir}/locale/ko/man
%lang(nl) %{_datadir}/locale/nl/man
%lang(pl) %{_datadir}/locale/pl/man
%lang(pt) %{_datadir}/locale/pt/man
%lang(ro) %{_datadir}/locale/ro/man
%lang(ru) %{_datadir}/locale/ru/man
%lang(sl) %{_datadir}/locale/sl/man
