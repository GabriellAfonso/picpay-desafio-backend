import { DOM } from "../utils/domElements.js";
import { updateHtmlContent } from "../utils/updateHtmlContent.js";

export class TransactionUI {
    showError(message) {
        DOM.transactionResponse.style.color = '#dc3545';
        DOM.transactionResponse.textContent = message;
        DOM.transactionResponse.style.display = 'block';
    }

    showSuccess(message) {
        DOM.transactionResponse.style.color = '#198754';
        DOM.transactionResponse.textContent = message;
        DOM.transactionResponse.style.display = 'block';
    }

    clearInputs() {
        DOM.documentTransactionInput.value = '';
        DOM.valueTransactionInput.value = '';
    }

    hideModal() {
        DOM.confirmationModal.hide();
    }

    showModal(text) {
        DOM.confirmationModalText.textContent = text;
        DOM.confirmationModal.show();
    }

    async updateContent() {
        await updateHtmlContent('#balance-value')
        await updateHtmlContent('#transaction-history')
    }
}
