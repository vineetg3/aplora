import NodeWebSocket from 'ws';
import { p as packageVersion } from './background.js';
import 'https://cdn.jsdelivr.net/npm/socket.io-client@4.7.1/+esm';
import 'https://cdn.jsdelivr.net/npm/p-queue@8.0.1/+esm';

/**
 * @license
 * Copyright 2018 Google Inc.
 * SPDX-License-Identifier: Apache-2.0
 */
/**
 * @internal
 */
class NodeWebSocketTransport {
    static create(url, headers) {
        return new Promise((resolve, reject) => {
            const ws = new NodeWebSocket(url, [], {
                followRedirects: true,
                perMessageDeflate: false,
                // @ts-expect-error https://github.com/websockets/ws/blob/master/doc/ws.md#new-websocketaddress-protocols-options
                allowSynchronousEvents: false,
                maxPayload: 256 * 1024 * 1024, // 256Mb
                headers: {
                    'User-Agent': `Puppeteer ${packageVersion}`,
                    ...headers,
                },
            });
            ws.addEventListener('open', () => {
                return resolve(new NodeWebSocketTransport(ws));
            });
            ws.addEventListener('error', reject);
        });
    }
    #ws;
    onmessage;
    onclose;
    constructor(ws) {
        this.#ws = ws;
        this.#ws.addEventListener('message', event => {
            if (this.onmessage) {
                this.onmessage.call(null, event.data);
            }
        });
        this.#ws.addEventListener('close', () => {
            if (this.onclose) {
                this.onclose.call(null);
            }
        });
        // Silently ignore all errors - we don't know what to do with them.
        this.#ws.addEventListener('error', () => { });
    }
    send(message) {
        this.#ws.send(message);
    }
    close() {
        this.#ws.close();
    }
}

export { NodeWebSocketTransport };
