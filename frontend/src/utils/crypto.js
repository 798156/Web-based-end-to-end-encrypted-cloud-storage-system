
const CryptoUtils = {
    // 1. 生成 RSA 密钥对
    async generateKeyPair() {
        return await window.crypto.subtle.generateKey(
            {
                name: "RSA-OAEP",
                modulusLength: 2048,
                publicExponent: new Uint8Array([1, 0, 1]),
                hash: "SHA-256"
            },
            true,
            ["encrypt", "decrypt"]
        );
    },

    // 2. 从密码派生对称密钥 (PBKDF2)
    async deriveKeyFromPassword(password, salt) {
        const textEncoder = new TextEncoder();
        const passwordBuffer = textEncoder.encode(password);
        const saltBuffer = typeof salt === 'string' ? this.hexToArrayBuffer(salt) : salt;

        const importedKey = await window.crypto.subtle.importKey(
            "raw",
            passwordBuffer,
            "PBKDF2",
            false,
            ["deriveKey"]
        );

        return await window.crypto.subtle.deriveKey(
            {
                name: "PBKDF2",
                salt: saltBuffer,
                iterations: 100000,
                hash: "SHA-256"
            },
            importedKey,
            { name: "AES-GCM", length: 256 },
            true,
            ["encrypt", "decrypt"]
        );
    },

    // 3. 生成随机 AES 密钥
    async generateFileKey() {
        return await window.crypto.subtle.generateKey(
            { name: "AES-GCM", length: 256 },
            true,
            ["encrypt", "decrypt"]
        );
    },

    // 4. AES-GCM 加密
    async encryptData(dataBuffer, key) {
        const iv = window.crypto.getRandomValues(new Uint8Array(12));
        const encrypted = await window.crypto.subtle.encrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            key,
            dataBuffer
        );
        return {
            encrypted: encrypted,
            iv: iv
        };
    },

    // 5. AES-GCM 解密
    async decryptData(encryptedBuffer, key, iv) {
        return await window.crypto.subtle.decrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            key,
            encryptedBuffer
        );
    },

    // 6. RSA 加密
    async encryptKeyWithPublicKey(keyToEncrypt, publicKey) {
        const exportedKey = await window.crypto.subtle.exportKey("raw", keyToEncrypt);
        return await window.crypto.subtle.encrypt(
            { name: "RSA-OAEP" },
            publicKey,
            exportedKey
        );
    },

    // 7. RSA 解密
    async decryptKeyWithPrivateKey(encryptedKeyBuffer, privateKey) {
        const decryptedKeyBuffer = await window.crypto.subtle.decrypt(
            { name: "RSA-OAEP" },
            privateKey,
            encryptedKeyBuffer
        );
        return await window.crypto.subtle.importKey(
            "raw",
            decryptedKeyBuffer,
            { name: "AES-GCM", length: 256 },
            true,
            ["encrypt", "decrypt"]
        );
    },

    // --- Helpers ---

    async exportKey(key) {
        const format = key.type === "public" ? "spki" : (key.type === "private" ? "pkcs8" : "raw");
        const exported = await window.crypto.subtle.exportKey(format, key);
        return this.arrayBufferToBase64(exported);
    },

    async importKey(base64Key, type) {
        const buffer = this.base64ToArrayBuffer(base64Key);
        if (type === "public") {
            return await window.crypto.subtle.importKey(
                "spki", buffer,
                { name: "RSA-OAEP", hash: "SHA-256" },
                true, ["encrypt"]
            );
        } else if (type === "private") {
            return await window.crypto.subtle.importKey(
                "pkcs8", buffer,
                { name: "RSA-OAEP", hash: "SHA-256" },
                true, ["decrypt"]
            );
        } else {
             return await window.crypto.subtle.importKey(
                "raw", buffer,
                { name: "AES-GCM" },
                true, ["encrypt", "decrypt"]
            );
        }
    },

    arrayBufferToBase64(buffer) {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    },

    base64ToArrayBuffer(base64) {
        const binary_string = window.atob(base64);
        const len = binary_string.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binary_string.charCodeAt(i);
        }
        return bytes.buffer;
    },

    generateSalt() {
        const array = new Uint8Array(16);
        window.crypto.getRandomValues(array);
        return this.arrayBufferToHex(array);
    },

    arrayBufferToHex(buffer) {
        return Array.from(new Uint8Array(buffer))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    },

    hexToArrayBuffer(hex) {
        const bytes = new Uint8Array(hex.length / 2);
        for (let i = 0; i < hex.length; i += 2) {
            bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
        }
        return bytes.buffer;
    },

    // 新增：支持 Unicode (中文) 的 Base64 编码
    unicodeToBase64(str) {
        return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, function(match, p1) {
            return String.fromCharCode('0x' + p1);
        }));
    },

    // 新增：支持 Unicode (中文) 的 Base64 解码
    base64ToUnicode(b64) {
        return decodeURIComponent(atob(b64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
    }
};

export default CryptoUtils;
