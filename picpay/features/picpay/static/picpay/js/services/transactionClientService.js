
export class TransactionService {
    constructor({ api, transactionUI, transactionValidator }) {
        this.api = api
        this.ui = transactionUI
        this.validator = transactionValidator
    }

    async processTransaction(data) {
        this.validator.validate(data)
        const recipient = await this.getRecipientData(data.document)
        this.openConfirmationModal(recipient.complete_name, data.value)

    }
    async sendTransaction(data) {
        const endpoint = 'transaction/'
        const response = await this.api.post(endpoint, data)
        await this.transactionResponse(response)
        await this.ui.updateContent()
        this.ui.hideModal()
    }
    openConfirmationModal(name, value) {
        this.ui.showModal(`Deseja transferir R$: ${value} para ${name}`)
    }

    async getRecipientData(document) {
        const endpoint = `recipient-preview/?document=${encodeURIComponent(document)}`
        const response = await this.api.get(endpoint)
        return response
    }

    async transactionResponse(response) {
        if (response.error) {
            this.ui.showError(response.error)
        }
        if (response.success) {
            this.ui.showSuccess(response.success)
            this.ui.clearInputs()
        }
    }

}

//clica no botao de enviar dinheiro
//pega o nome completo do receiver a quem vc esta tentando enviar o dinheiro
//perunta "vc deseja enviar x valor a fulano?"
//se sim envia transaçao pra ser tratada pelo servidor