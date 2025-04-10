class RecorderProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = [];
    this.chunkSize = 16000 * 0.5;
  }

  process(inputs) {
    const input = inputs[0][0];
    if (!input) return true;

    for (let i = 0; i < input.length; i++) {
      const s = Math.max(-1, Math.min(1, input[i]));
      this.buffer.push(s * 0x7fff);
    }

    if (this.buffer.length >= this.chunkSize) {
      const int16 = new Int16Array(this.buffer);
      this.port.postMessage(int16.buffer);
      this.buffer = [];
    }

    return true;
  }
}

registerProcessor("recorder-processor", RecorderProcessor);
