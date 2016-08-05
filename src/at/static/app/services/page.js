app.factory('PageService', function($http) {

    /*
    var pages = [
        {
            name: 'My Dashboard',
            slug: 'my-dashboard',
            widgets: [
                { id: 1, type: 'widget-fitness', params: {}},
                { id: 4, type: 'widget-fitness-add', params: {}},
                { id: 2, type: 'widget-gallery', params: { path: '/Users/phili/IdeaProjects/entrance/at/static/assets/gallery/', galleryName: 'X-Rays' }},
                { id: 3, type: 'widget-fitness-list', params: {}}
            ]
        }
    ];
    */

    return {
        Page: function (name, slug, widgets) {
            return {
                name: name,
                slug: slug,
                widgets: widgets
            };
        },
        Widget: function (id, type, params) {
            return {
                id: id,
                type: type,
                params: params
            }
        },
        pages: [],
        getPage: function (slug) {
            for (var i=0; i < this.pages.length; i++) {
                if (this.pages[i].slug == slug)
                    return this.pages[i];
            }
            return null;
        },
        createPage: function (name) {
            var slug = slugify(name);
            if (this.getPage(slug) != null) {
                var i = 1;
                var altSlug = slug + '-' + i;
                while (this.getPage(altSlug) != null) {
                    i++;
                    altSlug = slug + '-' + i;
                }
                slug = altSlug;
                name = name + '-' + i;
            }
            this.pages.push(this.Page(name, slug, []));
            this.pushPages();
        },
        removePage: function (slug) {
            var page = this.getPage(slug);
            if (page == null)
                return;
            this.pages.splice(this.pages.indexOf(page), 1);
            this.pushPages();
        },
        getWidget: function (slug, id) {
            var page = this.getPage(slug);
            if (page == null)
                return;
            for (var i=0; i < page.widgets.length; i++) {
                if (id == page.widgets[i].id)
                    return page.widgets[i];
            }
            return null;
        },
        sortWidgets: function (slug, order) {
            var page = this.getPage(slug);
            if (page == null)
                return;
            var widgets = [];
            for (var i=0; i < order.length; i++)
                widgets[i] = this.getWidget(slug, order[i]);
            page.widgets = widgets;
            this.pushPages();
        },
        addWidget: function (slug, widget, params) {
            var page = this.getPage(slug);
            if (page == null)
                return;

            var i=0;
            while (this.getWidget(slug, i) != null)
                i++;

            page.widgets.push(this.Widget(i, widget, params));
            this.pushPages();
        },
        removeWidget: function (slug, id) {
            var page = this.getPage(slug);
            if (page == null)
                return;

            var widget = this.getWidget(page.slug, id);
            if (widget == null)
                return;

            page.widgets.splice(page.widgets.indexOf(widget), 1);
            this.pushPages();
        },
        getPages: function () {
            return $http.get(baseUrl + '/pages/');
        },
        pushPages: function () {
            $http.post(baseUrl + '/pages/', this.pages)
                .success(function (data) {
                })
                .error(function (data) {
                });
        }
    };

    function slugify(string) {
        return string.replace(' ', '-');
    }

});