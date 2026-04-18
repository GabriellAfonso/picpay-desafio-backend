import { DOM } from "../utils/domElements.js";



export class DataTransactionValidator {
    constructor() {

    }

    validate(data) {
        this.validateDocument(data.document)
        this.validateValue(data.value)
    }

    validateDocument(document) {
        if (document.length < 11 || document.length > 14) {
            DOM.transactionResponse.style.color = '#dc3545';
            DOM.transactionResponse.textContent = 'Documento invalido!';
            DOM.transactionResponse.style.display = 'block';
            throw new Error("Documento invalido");
        }
    }
    validateValue(value) {
        if (value <= 0) {
            DOM.transactionResponse.style.color = '#dc3545';
            DOM.transactionResponse.textContent = 'Valor invalido!';
            DOM.transactionResponse.style.display = 'block';
            throw new Error("Valor invalido");
        }

    }



}