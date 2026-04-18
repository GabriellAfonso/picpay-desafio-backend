export class ApiCommunicator {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async get(endpoint) {
        return this.#request('GET', endpoint);
    }

    async post(endpoint, payload) {
        return this.#request('POST', endpoint, payload);
    }

    async patch(endpoint, payload) {
        return this.#request('PATCH', endpoint, payload);
    }

    async uploadFile(endpoint, file, fieldName = 'file') {
        const formData = new FormData();
        formData.append(fieldName, file);
        return this.#request('PATCH', endpoint, formData, false);
    }

    async #request(method, endpoint, payload = null, isJson = true) {
        const requestUrl = `${this.baseURL}${endpoint}`;
        const options = this.#buildOptions(method, payload, isJson);

        try {
            const response = await fetch(requestUrl, options);
            const data = await response.json();

            if (response.status >= 500) {
                throw new Error('Erro ao fazer a solicitação à API');
            }

            return data;
        } catch (error) {
            console.error('Erro na requisição:', error.message);
            throw error;
        }
    }

    #buildOptions(method, payload, isJson) {
        const headers = this.#buildHeaders(isJson);

        const options = {
            method,
            headers,
        };

        if (payload) {
            options.body = isJson ? JSON.stringify(payload) : payload;
        }

        return options;
    }

    #buildHeaders(isJson) {
        const headers = {
            'X-CSRFToken': this.#getCSRFToken(),
        };

        if (isJson) {
            headers['Content-Type'] = 'application/json';
        }

        return headers;
    }

    #getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (const cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return null;
    }
}
