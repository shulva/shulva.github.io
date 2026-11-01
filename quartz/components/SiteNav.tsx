import { QuartzComponent, QuartzComponentConstructor } from "./types"

const SiteNav: QuartzComponent = ({ fileData }) => {
  const cv = fileData.slug === "index"
  return (
    <nav class="site-nav" aria-label="Primary">
      <a href="/" aria-current={cv ? "page" : undefined}>CV</a>
      <a href="/notes/" aria-current={!cv ? "page" : undefined}>NOTES</a>
    </nav>
  )
}
export default (() => SiteNav) satisfies QuartzComponentConstructor
