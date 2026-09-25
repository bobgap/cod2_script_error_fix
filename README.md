Not sure if this also fixes iwdmismatches.  This primarily fixes scripting errors due to code conflicts, but might also fix some mismatches...

The Call of Duty suite of games, and specifically for this repository, Call of Duty 2 (CoD2), features the ability to create custom maps.  The author is administrator of a server where we have 1400+ maps available to place in rotation.  Each of these maps uses multiple files to make the map function.  

This work-around is to handle the gsc files, the "game scripting files," that conflict with each other by renaming the files that conflict and altering the routine calls to the renamed file.

Each map has the opportunity (not required) to provide a top-level gsc file, in the form "mapname.gsc", where mapname is the name of the map.  This top-level gsc may call routines in other files.  GSC files reside in maps/mp/, which is a flat directory, available to all the processes on the server:
***Sample of gsc files in the stock game:
maps/mp/_utility.gsc
maps/mp/mp_matmata_fx.gsc
maps/mp/mp_dawnville.gsc
maps/mp/gametypes/_hud_teamscore.gsc
...
maps/mp/mp_downtown.gsc
maps/mp/mp_burgundy.gsc
maps/mp/mp_trainstation.gsc
When a map is started, it loads the files in its iwd into the game directory.

GSC files with the same name may conflict in the client's suite of downloaded custom maps, the file first loaded is the one that is used.  One can see what this order is by viewing the game logs.

When running a mod, the mod folder, called fs_game, is added to this file structure and is loaded quite high in the order, so it may be used to gain precedence over the other files in the game.  Taking advantage of this, a maps/mp directory may be added to the fs_game folder, containing the gsc files needed to be modified to change map functionality, such as adding/removing spawnpoints, adding killzones, etc..  The fs_game directory for our server is o3a:
/home/server/o3a/
and its maps/mp folder is:
/home/server/o3a/maps/mp

When a client joins the server, it checks the files by calculating a checksum of the files that exist in the client's local iwd files.  If the sum of one of the files does not match that of the files on the server for this map, it flags an iwd mismatch.  I am guessing that since I am changing a gsc file name, the corresponding gsc file that had the old name is no longer is flagged for iwd mismatch.

One of the more prevalent files that cause IWD sum/mismatch errors is barrels.gsc.  There are 22 different barrels.gsc files in the 1400 map files on our server, so if we load a map containing a barrels.gsc file, it will grab the first it comes to in the client iwds, which may be in conflict and cause an error.

So what I did, after much contemplationg, is to
1. Search for all gsc files in our custom maps (all custom maps were unzipped into unzippedcustomiwds, each map having its own directory.  GSC files are located in the maps/mp subdirectory for that map (in this case, mp_d_day):   unzippedcustomiwds/mp_d_day/maps/mp
2. Look through each of the gsc files for calls to subroutines, (eliminating stock subroutines), then recursively search for calls to subroutines from within the top-level gsc files.
3. Take the results of this list of subroutines and the files containing them, group the files by md5sum, then create rename the gsc files, giving them unique names, for those that have the same name but different md5sums.  Renaming files that conflict with others (renamed by adding an "x" and a 6 bit portion of the md5sum). Sample:  barrels.gsc becomes barrelsx11d0f4.gsc barrels.gsc becomes barrelsx219115.gsc.
4. Modify the calling file so that the routine being called has its containing file renamed to match those in step 3.
5. Merge these files, manually, with those that may already exist in the fs_game/maps/mp directory that were changed for other reasons.

Since I have done this, client script errors have been virtually eliminated, and IWD sum/mismatch errors seem to be reducecd.

I undoubtedly have some misunderstandings about how this works, but what I have done seems to have solved a problem.  All the maps with exploding barrels once again have exploding barrels and IWD sum/mismatch errors are reduced.
