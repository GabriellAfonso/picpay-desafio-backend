export const MaskDocument = {
    apply: function (selector) {
        const $el = $(selector);
        const masks = ['000.000.000-009', '00.000.000/0000-00'];

        $el.mask(masks[0], {
            onKeyPress: function (val, e, field, options) {
                const mask = val.replace(/\D/g, '').length > 11 ? masks[1] : masks[0];
                $el.mask(mask, options);
            }
        });
    }
}
