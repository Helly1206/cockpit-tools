#!/bin/bash
NAME="tools"
LNAME="cockpit-$NAME"
USRDIR="/usr"
CKPTDIR="share/cockpit"
USRLOC="$USRDIR/$CKPTDIR/$NAME"
DEBFOLDER="debian"

minify_install () {
    echo "Installing and compiling files"
    
    which minify >/dev/null
    if [ $? -ne 0 ]; then
        echo "Minify not installed. Install minify first"
        echo "e.g. by: sudo apt install minify"
        exit
    fi
    
    minify -r -o ".$USRLOC" --match="\.js" $NAME
    #minify -r -o ".$USRLOC" --match="\.css" $NAME
    #minify -r -o ".$USRLOC" --match="\.html" $NAME
    cp "$NAME/tools.css" ".$USRLOC/"
    cp "$NAME/tools.html" ".$USRLOC/"
    cp "$NAME/manifest.json" ".$USRLOC/"
}

if [ "$EUID" -ne 0 ]
then
	echo "Please execute as root ('sudo install.sh' or 'sudo make install')"
	exit
fi

if [ "$1" == "-u" ] || [ "$1" == "-U" ]
then
	echo "$LNAME uninstall script"

    echo "Removing files"
	if [ -d "$USRLOC" ]; then
        rm -rf "$USRLOC"
    fi

elif [ "$1" == "-h" ] || [ "$1" == "-H" ]
then
	echo "Usage:"
	echo "  <no argument>: install $NAME"
	echo "  -u/ -U       : uninstall $NAME"
	echo "  -h/ -H       : this help file"
	echo "  -d/ -D       : build debian package"
	echo "  -c/ -C       : Cleanup compiled files in install folder"
elif [ "$1" == "-c" ] || [ "$1" == "-C" ]
then
	echo "$LNAME Deleting compiled files in install folder"
	rm -f ".$USRLOC"/*
	rm -f ./*.deb
	rm -rf "$DEBFOLDER"/$LNAME
	rm -rf "$DEBFOLDER"/.debhelper
	rm -f "$DEBFOLDER"/files
	rm -f "$DEBFOLDER"/files.new
	rm -f "$DEBFOLDER"/$LNAME.*
elif [ "$1" == "-d" ] || [ "$1" == "-D" ]
then
	echo "$LNAME build debian package"
	minify_install
	fakeroot debian/rules clean binary
	mv ../*.deb .
else
	echo "$LNAME install script"
    minify_install
    
    if [ ! -d "$USRLOC" ]; then
        mkdir "$USRLOC"
    fi
    cp -r ".$USRLOC/." "$USRLOC/"
	
    
fi
