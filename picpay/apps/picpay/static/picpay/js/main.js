import { ApiCommunicator } from "./services/apiCommunicatorService.js";
import { TransactionService } from "./services/transactionClientService.js";
import { ProfileUI } from "./ui/profileUi.js";
import { TransactionUI } from "./ui/transactionUi.js";
import { DOM } from "./utils/domElements.js";
import { DataTransactionValidator } from "./validators/dataTransactionValidator.js";


const profileUI = new ProfileUI
const API = new ApiCommunicator(window.location.origin + '/picpay/api/')
const transactionService = new TransactionService({
    api: API,
    transactionUI: new TransactionUI,
    transactionValidator: new DataTransactionValidator,
})

document.getElementById('transaction-tab-btn').addEventListener('click', () => {
    profileUI.openTab('transaction')
});
document.getElementById('transaction-tab-arrow').addEventListener('click', () => {
    profileUI.closeTab('transaction')
});

document.getElementById('transaction-btn').addEventListener('click', () => {
    var data = {
        document: DOM.documentTransactionInput.value,
        value: DOM.valueTransactionInput.value,
    }
    transactionService.processTransaction(data)
});
document.getElementById('confirmation-modal-btn').addEventListener('click', () => {
    var data = {
        document: DOM.documentTransactionInput.value,
        value: DOM.valueTransactionInput.value,
    }
    transactionService.sendTransaction(data)
});
