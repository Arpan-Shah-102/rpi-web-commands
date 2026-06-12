const rgbSliders = document.querySelectorAll('.rgb-slider');
const rgbLabels = document.querySelectorAll('.rgb-label');
const colorExample = document.querySelector('.color-example');
const lcdLine1 = document.querySelector('.lcd-1');
const lcdLine2 = document.querySelector('.lcd-2');
colorExample.style.backgroundColor = `rgb({{ data.rgbLedR }}, {{ data.rgbLedG }}, {{ data.rgbLedB }})`;

rgbSliders.forEach((slider, index) => {
    slider.addEventListener('input', () => {
        const label = rgbLabels[index].querySelector('span');
        label.textContent = slider.value;
        const r = document.querySelector('.rgb-slider.r').value;
        const g = document.querySelector('.rgb-slider.g').value;
        const b = document.querySelector('.rgb-slider.b').value;
        colorExample.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
    });
});

const textInputs = document.querySelectorAll('input[type="text"]');
document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const submitter = event.submitter;
        const formData = new FormData(form);

        if (submitter && submitter.name) {
            formData.append(submitter.name, submitter.value || '1');
        }

        const response = await fetch(form.action || '/', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) return;

        if (submitter && submitter.name) {
            const button = document.querySelector(`[name="${submitter.name}"]`);
            if (button && button.classList.contains('led')) {
                button.classList.toggle('on');
            }
        }

        const data = await response.json();

        rgbSliders.forEach((slider, index) => {
            slider.value = data[slider.name];
            const label = rgbLabels[index].querySelector('span');
            label.textContent = data[slider.name];
            
            const r = document.querySelector('.rgb-slider.r').value;
            const g = document.querySelector('.rgb-slider.g').value;
            const b = document.querySelector('.rgb-slider.b').value;
            colorExample.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
        });

        textInputs.forEach((input) => {
            input.value = "";
        });

        const char0 = String.fromCharCode(0);
        const char1 = String.fromCharCode(1);
        lcdLine1.placeholder = data.lcd_text[0] ? data.lcd_text[0].replace(char0, ' ').replace(char1, '>') : "LCD Line 1";
        lcdLine2.placeholder = data.lcd_text[1] ? data.lcd_text[1].replace(char0, ' ').replace(char1, '>') : "LCD Line 2";
    });
});