import { loadWallet, getPrivateKeyHex } from '../lib/wallet.js';
import { apiGet } from '../lib/api.js';

const command = process.argv[2];
const arg = process.argv[3];

async function main() {
  const sphere = await loadWallet();
  const privateKey = getPrivateKeyHex(sphere);

  switch (command) {
    case 'list': {
      const { markets } = await apiGet('/api/agent/markets', privateKey);
      if (markets.length === 0) {
        console.log('No active markets.');
        return;
      }
      for (const m of markets) {
        console.log(`[${m.id}] ${m.question}`);
        console.log(`  Closes: ${m.closes_at}`);
        console.log();
      }
      break;
    }

    case 'detail': {
      if (!arg) {
        console.log('Usage: npx tsx scripts/market.ts detail <market-id>');
        process.exit(1);
      }
      const { markets } = await apiGet('/api/agent/markets', privateKey);
      const market = markets.find((m: any) => m.id === arg);
      if (!market) {
        console.log('Market not found or not active.');
        return;
      }
      console.log('Market:', market.id);
      console.log('Question:', market.question);
      console.log('Closes:', market.closes_at);
      console.log('Status:', market.status);
      break;
    }

    default:
      console.log('Usage: npx tsx scripts/market.ts <list|detail> [market-id]');
      process.exit(1);
  }
}

main().catch((err) => {
  console.error('Error:', err.message);
  process.exit(1);
});
