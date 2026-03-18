// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview

client<llm> CustomGPT4o {
  provider openai
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY
  }
}

client<llm> CustomGPT4oMini {
  provider openai
  retry_policy Exponential
  options {
    model "gpt-4o-mini"
    api_key env.OPENAI_API_KEY
  }
}

client<llm> CustomSonnet {
  provider anthropic
  options {
    model "claude-3-5-sonnet-20241022"
    api_key env.ANTHROPIC_API_KEY
  }
}


client<llm> CustomHaiku {
  provider anthropic
  retry_policy Constant
  options {
    model "claude-3-haiku-20240307"
    api_key env.ANTHROPIC_API_KEY
  }
}

// MiniMax M2.7 - latest high-capability model (recommended)
// Uses OpenAI-compatible API: https://www.minimaxi.com/
client<llm> MiniMaxM27 {
  provider openai
  options {
    model "MiniMax-M2.7"
    api_key env.MINIMAX_API_KEY
    base_url "https://api.minimax.io/v1"
  }
}

// MiniMax M2.7-highspeed - faster variant optimized for low-latency tasks
client<llm> MiniMaxM27Highspeed {
  provider openai
  retry_policy Exponential
  options {
    model "MiniMax-M2.7-highspeed"
    api_key env.MINIMAX_API_KEY
    base_url "https://api.minimax.io/v1"
  }
}

// MiniMax M2.5 - previous generation model with 204K context window
client<llm> MiniMaxM25 {
  provider openai
  options {
    model "MiniMax-M2.5"
    api_key env.MINIMAX_API_KEY
    base_url "https://api.minimax.io/v1"
  }
}

// MiniMax M2.5-highspeed - previous generation faster variant
client<llm> MiniMaxM25Highspeed {
  provider openai
  retry_policy Exponential
  options {
    model "MiniMax-M2.5-highspeed"
    api_key env.MINIMAX_API_KEY
    base_url "https://api.minimax.io/v1"
  }
}

// https://docs.boundaryml.com/docs/snippets/clients/round-robin
client<llm> CustomFast {
  provider round-robin
  options {
    // This will alternate between the two clients
    strategy [CustomGPT4oMini, CustomHaiku, MiniMaxM27Highspeed]
  }
}

// https://docs.boundaryml.com/docs/snippets/clients/fallback
client<llm> OpenaiFallback {
  provider fallback
  options {
    // This will try the clients in order until one succeeds
    strategy [CustomGPT4oMini, CustomGPT4oMini, MiniMaxM27]
  }
}

// https://docs.boundaryml.com/docs/snippets/clients/retry
retry_policy Constant {
  max_retries 3
  // Strategy is optional
  strategy {
    type constant_delay
    delay_ms 200
  }
}

retry_policy Exponential {
  max_retries 2
  // Strategy is optional
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 10000
  }
}