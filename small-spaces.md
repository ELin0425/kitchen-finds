---
layout: page
title: Small Kitchens and Gifts
permalink: /small-spaces/
---

Dorm rooms, first apartments, and shared kitchens all come with the same constraint: limited counter space, limited storage, and no budget for anything that only does one job. This hub is for cooking in a small space and for buying kitchen gifts for someone who's in one.

<ul class="hub-list">
  <li class="hub-list-item">
    {% assign p = site.posts | where: "category", "small-spaces" | where_exp: "p", "p.url contains 'college-students'" | first %}
    <h3><a href="{{ p.url | relative_url }}">{{ p.title | escape }}</a></h3>
    <p>Dorm and apartment kitchens rarely have more than a few square feet of usable counter space, so every gadget has to earn its spot. This roundup covers the picks that actually get used daily instead of collecting dust in a cabinet.</p>
  </li>
  <li class="hub-list-item">
    {% assign p = site.posts | where: "category", "small-spaces" | where_exp: "p", "p.url contains 'dorm-rooms'" | first %}
    <h3><a href="{{ p.url | relative_url }}">{{ p.title | escape }}</a></h3>
    <p>Most dorm rooms don't allow a full stove, so these mini appliances are chosen specifically for small footprints, low power draw, and dorm-policy-friendly designs that still let you cook a real meal.</p>
  </li>
  <li class="hub-list-item">
    {% assign p = site.posts | where: "category", "small-spaces" | where_exp: "p", "p.url contains 'kitchen-gifts'" | first %}
    <h3><a href="{{ p.url | relative_url }}">{{ p.title | escape }}</a></h3>
    <p>Kitchen gifts have a bad reputation for ending up in a drawer unused. These picks are built around things a home cook will actually reach for, whether they're setting up a first kitchen or just need a gift that isn't another mug.</p>
  </li>
</ul>

<p>Looking for something specific? Check our <a href="/guides/">kitchen guides</a> for maintenance tips that stretch the life of gear you already own, small kitchen or not.</p>
