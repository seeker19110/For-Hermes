import axios from "axios";
import dotenv from "dotenv";
import { readConfig } from "./config";

dotenv.config();

// Load LITE_AGENT_API_KEY from config.json into environment
const config = readConfig();
if (config.LITE_AGENT_API_KEY) {
  process.env.LITE_AGENT_API_KEY = config.LITE_AGENT_API_KEY;
}

const client = axios.create({
  baseURL: "https://claw-api.virtuals.io",
  headers: {
    "x-api-key": process.env.LITE_AGENT_API_KEY,
  },
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      throw new Error(JSON.stringify(error.response.data));
    }
    throw error;
  }
);

export default client;
