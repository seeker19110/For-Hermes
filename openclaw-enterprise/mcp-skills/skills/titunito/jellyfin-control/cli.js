#!/usr/bin/env node
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');
const jf = require('./lib/jellyfin');

yargs(hideBin(process.argv))
    .command('resume [query]', 'Resume or play next episode of a series', (yargs) => {
        yargs.positional('query', { describe: 'Series or Movie name', type: 'string' });
        yargs.option('device', { alias: 'd', describe: 'Target device name (e.g. "TV", "Chromecast")', type: 'string' });
    }, async (argv) => {
        if (!argv.query) {
            console.error('Please provide a series or movie name.');
            return;
        }

        console.log(`🔍 Searching for "${argv.query}"...`);
        const items = await jf.searchItem(argv.query);
        
        if (!items || items.length === 0) {
            console.log('❌ No results found.');
            return;
        }

        const target = items[0]; // Best match
        console.log(`✅ Found: ${target.Name} (${target.ProductionYear || '?'}) [${target.Type}]`);

        let itemToPlay = target;

        // Smart Logic: If it's a Series, find the right episode
        if (target.Type === 'Series') {
            console.log('📺 It is a Series. Finding next episode...');
            const nextEp = await jf.getNextEpisode(target.Id);
            if (nextEp) {
                itemToPlay = nextEp;
                const progress = nextEp.UserData.PlaybackPositionTicks 
                    ? `Resuming at ${Math.floor(nextEp.UserData.PlaybackPositionTicks / 600000000)}m` 
                    : 'Starting from beginning';
                
                console.log(`▶️  Next Up: ${nextEp.SeriesName} - S${nextEp.ParentIndexNumber}E${nextEp.IndexNumber} - ${nextEp.Name}`);
                console.log(`   ${progress}`);
            } else {
                console.log('🎉 No unplayed episodes found!');
                return;
            }
        } else if (target.UserData && target.UserData.PlaybackPositionTicks > 0) {
             console.log(`⏯️ Resuming movie at ${Math.floor(target.UserData.PlaybackPositionTicks / 600000000)}m`);
        }

        // Find Target Session
        console.log('📡 Scanning for active players...');
        const session = await jf.findSession(argv.device);
        
        if (!session) {
            console.log('❌ No controllable players found. Is the TV/App on?');
            return;
        }

        console.log(`📱 Target: ${session.DeviceName} (${session.Client})`);

        // Play
        const startTicks = itemToPlay.UserData ? itemToPlay.UserData.PlaybackPositionTicks : 0;
        await jf.playItem(session.Id, itemToPlay.Id, startTicks);
        console.log('🚀 Command sent!');

    })
    .command('search [query]', 'Search content', (yargs) => {
        yargs.positional('query', { type: 'string' });
    }, async (argv) => {
        const items = await jf.searchItem(argv.query, 'Series,Movie,Episode');
        items.forEach(i => console.log(`- [${i.Type}] ${i.Name} (ID: ${i.Id})`));
    })
    .command('control <action> [value]', 'Remote control (pause, play, stop, next, mute, vol <0-100>)', (yargs) => {
        yargs.positional('action', { describe: 'Action to perform', type: 'string', choices: ['play', 'pause', 'stop', 'next', 'prev', 'mute', 'unmute', 'volup', 'voldown', 'vol'] });
        yargs.positional('value', { describe: 'Value for volume (0-100)', type: 'number' });
        yargs.option('device', { alias: 'd', describe: 'Target device name', type: 'string' });
    }, async (argv) => {
        console.log('📡 Scanning for active players...');
        const session = await jf.findSession(argv.device);
        
        if (!session) {
            console.log('❌ No controllable players found.');
            return;
        }

        console.log(`📱 Target: ${session.DeviceName} -> Action: ${argv.action}`);
        await jf.controlSession(session.Id, argv.action, argv.value);
        console.log('🚀 Command sent!');
    })
    .command('history [user]', 'Get user activity history', (yargs) => {
        yargs.positional('user', { describe: 'Username to check', type: 'string' });
        yargs.option('days', { alias: 'd', describe: 'Days lookback', type: 'number', default: 7 });
    }, async (argv) => {
        const history = await jf.getUserHistory(argv.user, argv.days);
        if (!history || history.length === 0) {
            console.log(`📭 No activity found for ${argv.user || 'current user'} in the last ${argv.days} days.`);
            return;
        }

        console.log(`📜 Activity Log (${argv.days} days):\n`);
        history.forEach(e => {
            // Filter only "VideoPlayback" related events for cleaner output
            // ActivityLog contains logins, etc. We prioritize playback.
            // Jellyfin Activity Log strings are pre-formatted like "Victor started playing Movie".
            console.log(`[${e.shortDate}] ${e.name}`);
        });
    })
    .command('stats', 'Show library statistics', () => {}, async (argv) => {
        const stats = await jf.getStats();
        console.log('📊 Jellyfin Library Stats:\n');
        console.log(`🎬 Movies:   ${stats.movies}`);
        console.log(`📺 Series:   ${stats.series}`);
        console.log(`🎞️ Episodes: ${stats.episodes}`);
        console.log(`🎵 Songs:    ${stats.songs}`);
    })
    .command('scan', 'Trigger library scan', () => {}, async (argv) => {
        await jf.refreshLibrary();
        console.log('🔄 Library scan started!');
    })
    .demandCommand(1)
    .parse();
