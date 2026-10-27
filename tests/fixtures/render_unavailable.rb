require 'liquid'
require 'yaml'
require 'json'
require 'cgi'
module FixtureFilters
 def escape(x); CGI.escapeHTML(x.to_s); end
end
Liquid::Template.register_filter(FixtureFilters)
input = JSON.parse(STDIN.read)
source = File.read('_includes/UnavailableAttachments.html') rescue '{{ content }}'
puts Liquid::Template.parse(source, error_mode: :strict).render!({'content'=>input['html'], 'page'=>{'path'=>input['page']}, 'site'=>{'baseurl'=>'', 'data'=>{'unavailable_attachments'=>YAML.load_file('_data/unavailable_attachments.yml')}}})
