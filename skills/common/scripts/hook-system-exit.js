/*
Hook System.exit to prevent LicenseActivity from killing the game process.
Usage: frida -U -f com.kayac.BolaCapture -l hook-system-exit.js --no-pause
*/
Java.perform(function() {
    var System = Java.use('java.lang.System');
    System.exit.implementation = function(code) {
        console.log('[BolaCapture] System.exit called with code=' + code + ' - BLOCKING!');
        // Don't actually exit - just return
        // This only works if called from Java context
    };
});
