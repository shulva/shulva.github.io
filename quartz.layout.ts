import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [Component.SiteNav()],
  afterBody: [],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/shulva/shulva.github.io",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ArticleTitle(),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    Component.Explorer(),
  ],
  right: [
    Component.Graph(),
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer(),
  ],
  right: [Component.Graph(), Component.Backlinks()],
}

// Only the app-owned root is a CV; all note/demo/list pages retain Quartz tools.
for (const key of ["beforeBody", "left", "right"] as const) {
  defaultContentPageLayout[key] = defaultContentPageLayout[key].map((component) =>
    Component.ConditionalRender({ component, condition: (page) => page.fileData.slug !== "index" }),
  )
}
defaultContentPageLayout.beforeBody.unshift(Component.ConditionalRender({
  component: Component.ArticleTitle(), condition: (page) => page.fileData.slug === "index",
}))
