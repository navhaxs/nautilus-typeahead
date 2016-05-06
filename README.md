# nautilus-typeahead
This a testing fork of https://copr.fedorainfracloud.org/coprs/joelongjiamian/nautilus-typeahead/

Just trying to learn how to COPR/rpm building stuff works.

nautilus 3.18.5 with typeahead patch applied for Fedora 23.
(The default behaviour is rather odd!)

# Building steps

```shell
dnf download --source nautilus
# Unpack the rpm:
# nautilus-3.18.5.tar.xz file to ~/rpmbuild/SOURCES
# Also copy nautilus-interactive-search-3-18.patch to above dir.
#
# *.spec file probably should go in ~/rpmbuild/SPECS

# Make edits to original nautilus.spec to bump version number with
# new nautilus.spec

rpmlint nautilus.spec
dnf builddep nautilus.spec
rpmbuild -ba nautilus.spec 
cd ~/rpmbuild/RPMS/x86_64
sudo dnf reinstall nautilus-3.18.5-1.fc23.x86_64.rpm
gsettings set org.gnome.nautilus.preferences enable-interactive-search true
# rinse and repeat above for gtk3 package to also get the patched file chooser dialog
# gsettings set org.gtk.Settings.FileChooser use-type-ahead true
```
