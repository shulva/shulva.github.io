import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

const config: QuartzConfig = {
  configuration: {
    pageTitle: "Shulva · 知识花园",
    pageTitleSuffix: "",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "zh-CN",
    baseUrl: "shulva.github.io",
    ignorePatterns: ["private", "templates", ".obsidian"],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "local",
      cdnCaching: false,
      typography: { header: "system-ui", body: "system-ui", code: "monospace" },
      colors: {
        lightMode: { light: "#faf9f6", lightgray: "#e5e4df", gray: "#b8b8b8", darkgray: "#45484a", dark: "#252b2b", secondary: "#356b60", tertiary: "#628b78", highlight: "rgba(53,107,96,0.12)", textHighlight: "#d4e7bc88" },
        darkMode: { light: "#1d2323", lightgray: "#343d3c", gray: "#77817e", darkgray: "#c7d0ca", dark: "#ebefea", secondary: "#9acaba", tertiary: "#c0d5b4", highlight: "rgba(154,202,186,0.12)", textHighlight: "#6b874388" },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({ priority: ["frontmatter", "filesystem"] }),
      Plugin.SyntaxHighlighting({ theme: { light: "github-light", dark: "github-dark" }, keepBackground: false }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false, mermaid: false, enableYouTubeEmbed: false, enableVideoEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "relative" }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "mathjax" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [Plugin.ComponentResources(), Plugin.ContentPage(), Plugin.FolderPage(), Plugin.TagPage(), Plugin.ContentIndex({ enableSiteMap: true, enableRSS: false }), Plugin.Assets(), Plugin.Static(), Plugin.NotFoundPage()],
  },
}
export default config
