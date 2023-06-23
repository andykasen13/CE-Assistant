const fs = require("fs");
const appid = require("appid");

let str = "";
fs.readFile('HelloWorld.txt', 'utf-8', async (err, inputD) => {
    if(err) throw err;
    else {
        str = inputD.toString();
        let thing = await appid(inputD);
        str = "" + thing.appid;

        fs.writeFile('HelloWorld.txt', str, (err) => {
            if(err) throw err;
        })
    }
});
