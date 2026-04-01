// Streaming hash server — reads lines from stdin, writes uint32 hashes to stdout.
// Used by the Python buddy patcher to match Claude Code's Bun.hash() behavior.
import { createInterface } from 'node:readline'

const rl = createInterface({ input: process.stdin })
for await (const line of rl) {
  process.stdout.write(String(Number(BigInt(Bun.hash(line)) & 0xffffffffn)) + '\n')
}
