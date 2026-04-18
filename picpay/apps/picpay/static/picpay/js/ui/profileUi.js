import { DOM } from "../utils/domElements.js";
import { MaskDocument } from "../utils/MaskDocument.js";
import { MaskMoney } from "../utils/maskMoney.js";
export class ProfileUI {
    constructor() {
        this.transactionTab = document.getElementById("transaction-tab")

        MaskDocument.apply('#document-transaction-input');
        MaskMoney.apply("#value-transaction-input")
        this.createTabsObj()
    }

    openTab(tab) {
        const target = this.tabs[tab];
        if (!target) return;
        target.element.style.left = "0px";
    }

    closeTab(tab) {
        const target = this.tabs[tab];
        if (!target) return;
        target.element.style.left = "-100%";
        if (typeof target.onClose === 'function') target.onClose();
    }

    toggleTab(tab) {
        const target = this.tabs[tab];
        if (!target) return;
        const isOpen = target.element.style.left === "0px";
        isOpen ? this.closeTab(tab) : this.openTab(tab);
    }

    createTabsObj() {
        this.tabs = {
            transaction: {
                element: this.transactionTab,
                onClose: () => {
                    DOM.documentTransactionInput.value = ''
                    DOM.valueTransactionInput.value = ''
                }
            },
            // transactionHistory: {
            //     element: document.getElementById("transactionTab"),
            //     onClose: () => {
            //         this.documentTransactionInput.value = '';
            //         this.valueTransactionInput.value = '';
            //     }
            // },

        };
    }

}
