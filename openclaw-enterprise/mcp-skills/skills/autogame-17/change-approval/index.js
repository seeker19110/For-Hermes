const { sendCard } = require('../common/feishu-client');

async function requestApproval(title, description, context, approverId) {
    const card = {
        "config": { "wide_screen_mode": true },
        "header": {
            "title": { "tag": "plain_text", "content": `🛡️ Approval Required: ${title}` },
            "template": "orange"
        },
        "elements": [
            { "tag": "div", "text": { "tag": "lark_md", "content": description } },
            { "tag": "hr" },
            { "tag": "div", "text": { "tag": "lark_md", "content": `**Context:**\n${context}` } },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": { "tag": "plain_text", "content": "✅ Approve" },
                        "type": "primary",
                        "value": { "action": "approve", "id": Date.now().toString() }
                    },
                    {
                        "tag": "button",
                        "text": { "tag": "plain_text", "content": "❌ Reject" },
                        "type": "danger",
                        "value": { "action": "reject", "id": Date.now().toString() }
                    }
                ]
            }
        ]
    };

    console.log(`Sending approval request to ${approverId}...`);
    return await sendCard(approverId, card);
}

if (require.main === module) {
    const args = require('minimist')(process.argv.slice(2));
    // Usage: node request.js --title "Deploy" --desc "Deploy v2" --context "Diff..." --approver "ou_..."
    if (args.title && args.approver) {
        requestApproval(args.title, args.desc || '', args.context || '', args.approver)
            .then(res => console.log(JSON.stringify(res)))
            .catch(err => console.error(err));
    }
}
