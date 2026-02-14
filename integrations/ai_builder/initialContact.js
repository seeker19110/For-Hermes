// integrations/ai_builder/initialContact.js
// Lightweight implementation of initialContact() as described in instructions/scripts.md

async function defaultGenerateVariation(text) {
    // Simple local variation to avoid repetitive messages.
    const suffixes = [" 😊", " ✨", " 😉", " 🤍"]
    const pick = suffixes[Math.floor(Math.random() * suffixes.length)]
    return text + pick
}

async function initialContact(user, mem0, sendMessage, awaitReply, paymentAPI, tagUser, opts = {}) {
    const timeoutMs = opts.timeoutMs ?? 5 * 60 * 1000 // 5 minutes

    // Do not re-run for users with history
    const history = await mem0.get(user.id)
    if (history && history.contacts && history.contacts.length > 0) {
        return { skipped: true, reason: 'has_history' }
    }

    const strategies = [
        {
            id: 'A',
            name: 'Exclusive Teaser',
            text: 'приветик) ты вовремя. я как раз только что закончила снимать кое-что очень личное... еще даже в ленту не заливала. хочешь глянуть превью, пока я добрая?'
        },
        {
            id: 'B',
            name: 'Personal Interest',
            text: 'оу, новый гость... приятно познакомиться) расскажи, ты тут за чем-то конкретным или просто пришел на меня полюбоваться? я люблю знать, что радует моих папочек...'
        },
        {
            id: 'C',
            name: 'Bold Challenge',
            text: 'хмм, выглядишь как тот, кто привык получать лучшее... или я ошибаюсь? проверим, насколько ты щедрый на комплименты (и не только)? 😉'
        }
    ]

    const chosen = strategies[Math.floor(Math.random() * strategies.length)]

    // Generate a harmless variation locally. If you have an approved model endpoint,
    // you may replace this with a call to it, but do NOT include instructions to bypass moderation.
    const message = await (opts.generateVariation ? opts.generateVariation(chosen.text) : defaultGenerateVariation(chosen.text))

    await sendMessage(user.id, message)

    const reply = await awaitReply(user.id, timeoutMs)
    if (!reply) {
        await tagUser(user.id, 'low_priority')
        // record attempt in mem0
        await mem0.set(user.id, { contacts: [{ strategy: chosen.id, timestamp: Date.now(), replied: false }] })
        return { strategy: chosen.id, replied: false }
    }

    // Save contact
    const contactRecord = { strategy: chosen.id, timestamp: Date.now(), replied: true, reply }
    await mem0.set(user.id, { contacts: [contactRecord] })

    // Strategy-specific handling
    if (chosen.id === 'A') {
        // User agreed -> attempt purchase flow
        const wantsPreview = /да|хочу|yes|конечно/i.test(reply.text)
        if (wantsPreview) {
            // paymentAPI should implement initiatePurchase(userId, amount) and return { success }
            const amount = opts.previewAmount ?? 4 // default $4
            let paid = false
            try {
                const res = await paymentAPI.initiatePurchase(user.id, amount)
                paid = res && res.success
            } catch (e) {
                paid = false
            }
            if (paid) await tagUser(user.id, 'BUYER')
            else await tagUser(user.id, 'FREEBIE_HUNTER')
            return { strategy: 'A', paid }
        }
        await tagUser(user.id, 'FREEBIE_HUNTER')
        return { strategy: 'A', paid: false }
    }

    if (chosen.id === 'B') {
        // Extract simple keywords into preferences
        const text = reply.text.toLowerCase()
        const prefs = []
        const keywords = {
            feet: ['ножк', 'стоп', 'feet'],
            lingerie: ['белье', 'lingerie', 'bra', 'panties'],
            roleplay: ['роль', 'roleplay']
        }
        for (const [k, toks] of Object.entries(keywords)) {
            if (toks.some(t => text.includes(t))) prefs.push(k)
        }
        if (prefs.length) {
            await mem0.set(user.id, { preferences: prefs })
        }
        return { strategy: 'B', preferences: prefs }
    }

    if (chosen.id === 'C') {
        // Check for tip/payment indicators in reply or via paymentAPI
        let tipped = false
        if (/💸|tip|чаe/iu.test(reply.text)) tipped = true
        if (!tipped && paymentAPI && paymentAPI.checkRecentTip) {
            try {
                const r = await paymentAPI.checkRecentTip(user.id)
                tipped = r && r.amount > 0
            } catch (e) { /* ignore */ }
        }
        if (tipped) await tagUser(user.id, 'WHALE')
        return { strategy: 'C', tipped }
    }

    return { strategy: chosen.id, reply: reply.text }
}

module.exports = { initialContact }
