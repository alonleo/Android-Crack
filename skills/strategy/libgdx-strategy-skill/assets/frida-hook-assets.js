Java.perform(function() {
    try {
        var AssetManager = Java.use('android.content.res.AssetManager');
        AssetManager.open.overload('java.lang.String').implementation = function(name) {
            console.log('[ASSET] open: ' + name);
            return this.open(name);
        };
        AssetManager.open.overload('java.lang.String', 'int').implementation = function(name, mode) {
            console.log('[ASSET] open: ' + name + ' mode=' + mode);
            return this.open(name, mode);
        };
        console.log('[ASSET] hook installed');
    } catch (e) {
        console.log('[ASSET] error: ' + e);
    }
});
