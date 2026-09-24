The Call of Duty suite of games, and specifically for this repository, Call of Duty 2 (CoD2), features the ability to create custom maps.  The author is administrator of a server where we have 1400+ games available to place in rotation.  Each of these maps have multiple files available to make the map function.  This work-around is to handle the gsc files, the "game scripting files."
Each map has the opportunity to provide a top-level gsc file, in the form "mapname.gsc", where mapname is the name of the map.  This then may call other routines in other files.  The folder that the gsc files reside in is maps/mp/, which is a flat directory, available to all the processes on the server:
***Sample of gsc files in the stock game:
maps/mp/_utility.gsc
maps/mp/mp_matmata_fx.gsc
maps/mp/mp_dawnville.gsc
maps/mp/mp_burgundy_fx.gsc
maps/mp/mp_toujane_fx.gsc
maps/mp/gametypes/tdm.gsc
maps/mp/gametypes/_hud_teamscore.gsc
...
maps/mp/mp_downtown.gsc
maps/mp/mp_burgundy.gsc
maps/mp/mp_trainstation.gsc

GSC files with the same name may conflict, the file first loaded is the one that is used.  One can see what this order is by viewing the game logs.

When running a mod, the mod folder, called fs_game, is added to this file structure and is loaded quite high in the order, so it may be used to gain precedence over the other files in the game.  Taking advantage of this, an maps/mp directory may be added to the fs_game folder containing the gsc files we need to modify.  The fs_game directory for our server is o3a:
/home/server/o3a/
and the maps/mp folder is:
/home/server/o3a/maps/mp

When a client joins the server, it checks the files by calculating a checksum of the files that exist in your local iwd files.
One of the more prevalent files that cause IWD sum/mismatch errors is barrels.gsc.  There are 22 different barrels.gsc files in the 1400 map files on our server, so if we load a map containing a barrels.gsc file, it will grab the first it comes to, which is probably going to be in conflict and cause an error.

So what I did, after much contemplationg, is to
1. Search for all gsc files in our custom maps (unzipped all the custom maps into unzippedcustomiwds, each containing a directory for the map, and the maps/mp below (among others) *** unzippedcustomiwds/mp_d_day/maps/mp
2. Look through each of the gsc files for routine calls, eliminating stock calls, then recursively search for calls within the called files.
3. Take the results of this and create files with unique names for those that conflict with others (adding "x" and a 6 bit segment of the md5sum of each file.) Sample:  barrelsx11d0f4.gsc barrelsx219115.gsc barrelsx23f121.gsc barrelsx32ef92.gsc
4. Modify the calling file so that the routine being called has its location file renamed to match those in step 3.
5. Merge the generated files with those that may already exist in the fs_game/maps/mp directory, retaining other modifications that might have already been done.

Since I have done this, client IWD sum/mismatch errors have been greatly reducecd or eliminated, as far as I can tell.
