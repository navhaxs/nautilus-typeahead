%global glib2_version 2.45.7
%global gnome_desktop3_version 3.0.0
%global gtk3_version 3.18.5
%global libxml2_version 2.7.8
%global libexif_version 0.6.20
%global exempi_version 2.1.0
%global gobject_introspection_version 0.9.5
%global gsettings_desktop_schemas_version 3.8.0

Name:           nautilus
Summary:        File manager for GNOME with Typeahead Find
Version:        3.18.5
Release:        1%{?dist}
License:        GPLv2+
Group:          User Interface/Desktops
Source:         https://download.gnome.org/sources/%{name}/3.18/%{name}-%{version}.tar.xz

Patch0: nautilus-interactive-search-3-18.patch

URL:            https://wiki.gnome.org/Apps/Nautilus

BuildRequires:  pkgconfig(exempi-2.0) >= %{exempi_version}
BuildRequires:  pkgconfig(glib-2.0) >= %{glib2_version}
BuildRequires:  pkgconfig(gnome-desktop-3.0) >= %{gnome_desktop3_version}
BuildRequires:  pkgconfig(gobject-introspection-1.0) >= %{gobject_introspection_version}
BuildRequires:  pkgconfig(gsettings-desktop-schemas) >= %{gsettings_desktop_schemas_version}
BuildRequires:  pkgconfig(gtk+-3.0) >= %{gtk3_version}
BuildRequires:  pkgconfig(libexif) >= %{libexif_version}
BuildRequires:  pkgconfig(libxml-2.0) >= %{libxml2_version}
BuildRequires:  pkgconfig(tracker-sparql-1.0)
BuildRequires:  pkgconfig(x11)
BuildRequires:  /usr/bin/appstream-util
BuildRequires:  desktop-file-utils
BuildRequires:  gettext
BuildRequires:  intltool >= 0.40.6-2
BuildRequires:  libselinux-devel
BuildRequires:  libtool

Requires:       glib2%{_isa} >= %{glib2_version}
Requires:       gsettings-desktop-schemas%{_isa} >= %{gsettings_desktop_schemas_version}
Requires:       gtk3%{_isa} >= %{gtk3_version}
Requires:       gvfs%{_isa}
Requires:       libexif%{_isa} >= %{libexif_version}
# the main binary links against libnautilus-extension.so
# don't depend on soname, rather on exact version
Requires:       %{name}-extensions%{_isa} = %{version}-%{release}

# The selinux patch is here to not lose it, should go upstream and needs
# cleaning up to work with current nautilus git.
#Patch4:         nautilus-2.91.8-selinux.patch

%description
Nautilus is the file manager and graphical shell for the GNOME desktop
that makes it easy to manage your files and the rest of your system.
It allows to browse directories on local and remote filesystems, preview
files and launch applications associated with them.
It is also responsible for handling the icons on the GNOME desktop.

%package extensions
Summary:        Nautilus extensions library
License:        LGPLv2+
Group:          Development/Libraries

%description extensions
This package provides the libraries used by nautilus extensions.

%package devel
Summary:        Support for developing nautilus extensions
License:        LGPLv2+
Group:          Development/Libraries
Requires:       %{name}%{_isa} = %{version}-%{release}
Requires:       %{name}-extensions%{_isa} = %{version}-%{release}

%description devel
This package provides libraries and header files needed
for developing nautilus extensions.

%prep
%setup -q

%patch0 -p1
#%%patch4 -p1 -b .selinux

%build
CFLAGS="$RPM_OPT_FLAGS -g -DNAUTILUS_OMIT_SELF_CHECK" %configure --disable-more-warnings

# drop unneeded direct library deps with --as-needed
# libtool doesn't make this easy, so we do it the hard way
sed -i -e 's/ -shared / -Wl,-O1,--as-needed\0 /g' libtool

make %{?_smp_mflags} V=1

%install
%make_install

desktop-file-install --delete-original       \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications             \
  --add-only-show-in GNOME                                  \
  $RPM_BUILD_ROOT%{_datadir}/applications/*

rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/nautilus/extensions-3.0/*.la

# Update the screenshot shown in the software center
#
# NOTE: It would be *awesome* if this file was pushed upstream.
#
# See http://people.freedesktop.org/~hughsient/appdata/#screenshots for more details.
#
appstream-util replace-screenshots $RPM_BUILD_ROOT%{_datadir}/appdata/org.gnome.Nautilus.appdata.xml \
  https://raw.githubusercontent.com/hughsie/fedora-appstream/master/screenshots-extra/org.gnome.Nautilus/a.png \
  https://raw.githubusercontent.com/hughsie/fedora-appstream/master/screenshots-extra/org.gnome.Nautilus/b.png \
  https://raw.githubusercontent.com/hughsie/fedora-appstream/master/screenshots-extra/org.gnome.Nautilus/c.png 

%find_lang %name


%check
appstream-util validate-relax --nonet %{buildroot}/%{_datadir}/appdata/org.gnome.Nautilus.appdata.xml


%postun
if [ $1 -eq 0 ]; then
  glib-compile-schemas %{_datadir}/glib-2.0/schemas >&/dev/null || :
fi

%posttrans
glib-compile-schemas %{_datadir}/glib-2.0/schemas >&/dev/null || :

%post extensions -p /sbin/ldconfig

%postun extensions -p /sbin/ldconfig

%files  -f %{name}.lang
%doc AUTHORS NEWS README
%license COPYING
%{_datadir}/appdata/org.gnome.Nautilus.appdata.xml
%{_datadir}/applications/*
%{_bindir}/*
%{_datadir}/dbus-1/services/org.gnome.Nautilus.service
%{_datadir}/dbus-1/services/org.freedesktop.FileManager1.service
%{_datadir}/gnome-shell/search-providers/nautilus-search-provider.ini
%{_mandir}/man1/nautilus.1*
%{_libexecdir}/nautilus-convert-metadata
%{_datadir}/GConf/gsettings/nautilus.convert
%{_datadir}/glib-2.0/schemas/org.gnome.nautilus.gschema.xml
%dir %{_libdir}/nautilus/extensions-3.0
%{_libdir}/nautilus/extensions-3.0/libnautilus-sendto.so
%{_sysconfdir}/xdg/autostart/nautilus-autostart.desktop

%files extensions
%license COPYING.EXTENSIONS COPYING.LIB
%{_libdir}/libnautilus-extension.so.*
%{_libdir}/girepository-1.0/*.typelib
%dir %{_libdir}/nautilus

%files devel
%{_includedir}/nautilus
%{_libdir}/pkgconfig/*
%{_libdir}/*.so
%{_datadir}/gir-1.0/*.gir
%dir %{_datadir}/gtk-doc/
%dir %{_datadir}/gtk-doc/html/
%doc %{_datadir}/gtk-doc/html/libnautilus-extension/
