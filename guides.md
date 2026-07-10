---
layout: page
title: Kitchen Guides
permalink: /guides/
---

Not every kitchen problem is solved by buying something new. These guides cover the skills and maintenance habits that make the tools you already own last longer and work better.

<ul class="hub-list">
  <li class="hub-list-item">
    {% assign p = site.posts | where: "category", "guides" | where_exp: "p", "p.url contains 'sharpen-a-knife'" | first %}
    <h3><a href="{{ p.url | relative_url }}">{{ p.title | escape }}</a></h3>
    <p>Most people replace a knife long before it actually needs replacing. This guide walks through the honing-versus-sharpening question, when to reach for which tool, and how to get a genuinely sharp edge at home without ruining your blade.</p>
  </li>
  <li class="hub-list-item">
    {% assign p = site.posts | where: "category", "guides" | where_exp: "p", "p.url contains 'season-a-cast-iron'" | first %}
    <h3><a href="{{ p.url | relative_url }}">{{ p.title | escape }}</a></h3>
    <p>A cast iron skillet is only as good as its seasoning. This guide covers the wash, oil, and bake cycle that builds a durable, naturally non-stick surface, plus how to keep that seasoning intact through years of regular cooking.</p>
  </li>
</ul>

<p>More guides get added as we cover new kitchen maintenance topics. See our <a href="/how-we-pick/">product selection process</a> if you're here from a roundup post and want to know how we choose what to recommend.</p>
