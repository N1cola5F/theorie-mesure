import DefaultTheme from 'vitepress/theme'
import './custom.css'
import ConceptMap from './components/ConceptMap.vue'
import PreimageDemo from './components/PreimageDemo.vue'
import LimsupLiminf from './components/LimsupLiminf.vue'
import MeasureContinuity from './components/MeasureContinuity.vue'
import StepApprox from './components/StepApprox.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ConceptMap', ConceptMap)
    app.component('PreimageDemo', PreimageDemo)
    app.component('LimsupLiminf', LimsupLiminf)
    app.component('MeasureContinuity', MeasureContinuity)
    app.component('StepApprox', StepApprox)
  }
}
