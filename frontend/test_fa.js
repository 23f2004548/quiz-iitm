import { icon } from '@fortawesome/fontawesome-svg-core'
import { faLaptop } from '@fortawesome/free-solid-svg-icons'

try {
    const laptop = icon(faLaptop)
    console.log("Icon name:", laptop.iconName)
    console.log("HTML array exists:", Array.isArray(laptop.html))
    console.log("HTML length:", laptop.html.length)
    console.log("HTML content snippet:", laptop.html[0].substring(0, 100))
} catch (e) {
    console.error("Error calling FontAwesome:", e)
}
