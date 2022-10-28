cockpit-tools v0.83

cockpit-tools -- Add links to external webtools to cockpit
============= == === ===== == ======== ======== == =======

This plugin not heavily documented yet, but that is probably not necessary. It's a cockpit UI to show links to external tools in cockpit.

It uses cockpit-stdplgin as standard look and feel for this UI.

Tools can be added/ deleted in /etc/cockpit-tools.xml or via /opt/tools/tools-cli.py via command line. see /opt/tools/tools-cli.py -h for more info.

<toolname>
    <icon>/etc/whatever.png</icon>
    <ref>https://192.168.1.1/example</ref>
</toolname>

That's all for now ...

Please send Comments and Bugreports to hellyrulez@home.nl
