Java.perform(function() {
    try {
        var Typeface = Java.use('android.graphics.Typeface');
        Typeface.createFromAsset.overload('android.content.res.AssetManager', 'java.lang.String').implementation = function(am, path) {
            console.log('[FONT] createFromAsset path=' + path);
            return this.createFromAsset(am, path);
        };
        console.log('[FONT] hook installed');
    } catch (e) {
        console.log('[FONT] error: ' + e);
    }
});
