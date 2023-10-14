require 'net/https'
require 'json'

module Jekyll
  class GistTag < Liquid::Tag

    def initialize(tag_name, text, tokens)
      super
      @text = text.strip
    end

    def render(context)
      username, gist_id = @text.split
      gist_response = Net::HTTP.get(URI("https://api.github.com/gists/#{gist_id}"))
      gist_data = JSON.parse(gist_response)
      gist_url = gist_data['html_url']
      "<script src=\"#{gist_url}.js\"></script>"
    end

  end

  Liquid::Template.register_tag('gist', GistTag)
end