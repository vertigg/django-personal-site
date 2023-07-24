function update(playerClass, isChecked) {
    if (isChecked) {
        document.querySelectorAll(`.${playerClass}`).forEach(item => item.style.visibility = 'visible')
    } else {
        document.querySelectorAll(`.${playerClass}`).forEach(item => item.style.visibility = 'collapse')
    }
}