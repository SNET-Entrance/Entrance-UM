app.controller("ContactController", function($scope,
                                             $controller,
                                             ContactService,
                                             ContactPropertyService,
                                             ContactAttributeService
) {

    $scope.indices = {
        contacts: [],
        properties: [],
        attributes: []
    };

    ContactService.getContacts().success(function (data) {
        $scope.contacts = data;
        $scope.index();
    });

    $scope.addNewContact = function (name, email) {
        var contact = ContactService.Contact(name, email);

        var addBtn = $('#add-contact-btn');
        var oldClass = addBtn.attr('class');
        addBtn.attr('class', 'fa fa-circle-o-notch fa-spin');
        addBtn.parent().attr('disabled', true);

        $('#add-new-contact-name').val('').focus();
        $('#add-new-contact').val('');

        ContactService.createContact(contact)
            .success(function (data) {
                addBtn.attr('class', oldClass);
                addBtn.parent().attr('disabled', false);

                $scope.contacts.push(contact);
                contact.id = data.id;
                $scope.index();
            })
            .error(function (data) {
                $scope.contacts.splice($scope.contacts.indexOf(contact), 1);
            });
    };

    $scope.deleteContact = function (id) {
        var index = $scope.indices.contacts[id];
        var contact = $scope.contacts[index];
        $scope.contacts.splice(index, 1);

        ContactService.deleteContact(id)
            .success(function (data) {
                $scope.index();
            })
            .error(function (data) {
                $scope.contacts.push(contact);
                $scope.index();
            })
    };

    $scope.edit = function (e, o) {
        var parent = $(e.target);
        var target = '';

        if (parent.attr('class').indexOf('contact-name') > -1)
            target = 'contact-name';
        if (parent.attr('class').indexOf('property-key') > -1)
            target = 'property-key';
        if (parent.attr('class').indexOf('property-value') > -1)
            target = 'property-value';
        if (parent.attr('class').indexOf('attribute-name') > -1)
            target = 'attribute-name';

        var value = parent.text();
        var deleteIcon = parent.find('i').first();
        parent.empty();
        parent.append('<input id="edit-field" type="text">');
        var editField = $('#edit-field');
        editField.val(value);
        editField.focus();
        if (target == 'property-key')
            editField.css('text-align', 'right');

        editField.on('blur', function () {
            var newValue = editField.val();
            parent.empty();
            parent.append(deleteIcon, newValue);
            if (value == newValue) return;
            switch (target) {
                case 'contact-name':
                    $scope.contacts[$scope.indices.contacts[o.contact.id]].name = newValue;
                    ContactService.updateContact(o.contact.id, o.contact)
                        .success(function (data) { /* TODO: notify user */ })
                        .error(function (data) {
                            $scope.contacts[$scope.indices.contacts[o.contact.id]].name = value;
                            parent.empty();
                            parent.append(deleteIcon, value);
                        });
                    break;
                case 'property-key':
                    var contactIndex = $scope.indices.contacts[o.property.user_id];
                    var propIndex = $scope.indices.properties[o.property.id];
                    $scope.contacts[contactIndex].properties[propIndex].key = newValue;
                    ContactPropertyService.updateProperty(o.property.user_id, o.property.id, o.property)
                        .success(function (data) { /* TODO: notify user */ })
                        .error(function (data) {
                            $scope.contacts[contactIndex].properties[propIndex].key = value;
                            parent.empty();
                            parent.append(deleteIcon, value);
                        });
                    break;
                case 'property-value':
                    var contactIndex = $scope.indices.contacts[o.property.user_id];
                    var propIndex = $scope.indices.properties[o.property.id];
                    $scope.contacts[contactIndex].properties[propIndex].value = newValue;
                    ContactPropertyService.updateProperty(o.property.user_id, o.property.id, o.property)
                        .success(function (data) { /* TODO: notify user */ })
                        .error(function (data) {
                            $scope.contacts[contactIndex].properties[propIndex].value = value;
                            parent.empty();
                            parent.append(deleteIcon, value);
                        });
                    break;
                case 'attribute-name':
                    var contactIndex = $scope.indices.contacts[o.attribute.user_id];
                    var attrIndex = $scope.indices.attributes[o.attribute.id];
                    $scope.contacts[contactIndex].attributes[attrIndex].name = newValue;
                    ContactAttributeService.updateAttribute(o.attribute.user_id, o.attribute.id, o.attribute)
                        .success(function (data) { /* TODO: notify user */ })
                        .error(function (data) {
                            $scope.contacts[contactIndex].attributes[attrIndex].name = value;
                            parent.empty();
                            parent.append(deleteIcon, value);
                        });
                    break;
            }
        });
    };

    $scope.addNewProperty = function(contactId, propertyKey, propertyValue) {
        var newProperty = ContactPropertyService.Property(propertyKey, propertyValue, contactId);
        $scope.contacts[$scope.indices.contacts[contactId]].properties.push(newProperty);
        $('#' + contactId + '-contact-property-key').val('').focus();
        $('#' + contactId + '-contact-property-value').val('');

        ContactPropertyService.createProperty(contactId, newProperty)
            .success(function (data) {
                newProperty.id = data.id;
                $scope.index();
            })
            .error(function (data) {
                var index = $scope.contacts[$scope.indices.contacts[contactId]].properties.indexOf(newProperty);
                $scope.contacts[$scope.indices.contacts[contactId]].properties.splice(index, 1);
            });
    };

    $scope.deleteProperty = function (contactId, propId) {
        var index = $scope.indices.properties[propId];
        var prop = $scope.contacts[$scope.indices.contacts[contactId]].properties[index];
        $scope.contacts[$scope.indices.contacts[contactId]].properties.splice(index, 1);
        ContactPropertyService.deleteProperty(contactId, propId)
            .success(function (data) {
                // TODO: notify user?
                $scope.index();
            })
            .error(function (data) {
                $scope.contacts[$scope.indices.contacts[contactId]].properties.push(prop);
                // TODO: notify user?
                $scope.index();
            });
    };

    $scope.addNewAttribute = function (contactId, attributeName) {
        var newAttribute = ContactAttributeService.Attribute(contactId, attributeName);
        $scope.contacts[$scope.indices.contacts[contactId]].attributes.push(newAttribute);
        $('#' + contactId + '-contact-attribute-name').val('').focus();

        ContactAttributeService.createAttribute(contactId, newAttribute)
            .success(function (data) {
                newAttribute.id = data.id;
                $scope.index();
                $('.contact-attribute-name').each(function () {
                    var attrSuggestions = $(this).autocomplete('option', 'source');
                    if (attrSuggestions.indexOf(attributeName) == -1)
                        attrSuggestions.push(attributeName);
                });
            })
            .error(function (data) {
                var index = $scope.contacts[$scope.indices.contacts[contactId]].attributes.indexOf(newAttribute);
                $scope.contacts[$scope.indices.contacts[contactId]].attributes.splice(index, 1);
            });
    };

    $scope.deleteAttribute = function (contactId, attrId) {
        var index = $scope.indices.attributes[attrId];
        var attr = $scope.contacts[$scope.indices.contacts[contactId]].attributes[index];
        $scope.contacts[$scope.indices.contacts[contactId]].attributes.splice(index, 1);

        ContactAttributeService.deleteAttribute(contactId, attrId)
            .success(function (data) {
                // TODO: notify user?
                $scope.index();
                $('.contact-attribute-name').each(function () {
                    var attrSuggestions = $(this).autocomplete('option', 'source');
                    attrSuggestions.splice(attrSuggestions.indexOf(attr.name), 1);
                });
            })
            .error(function (data) {
                // TODO: notify user?
                $scope.contacts[$scope.indices.contacts[contactId]].attributes.push(attr);
                $scope.index();
            });
    };

    $scope.index = function() {
        for (var i=0; i < $scope.contacts.length; i++) {
            $scope.indices.contacts[$scope.contacts[i].id] = i;
            for (var j=0; j < $scope.contacts[i].properties.length; j++)
                $scope.indices.properties[$scope.contacts[i].properties[j].id] = j;
            for (var j=0; j < $scope.contacts[i].attributes.length; j++)
                $scope.indices.attributes[$scope.contacts[i].attributes[j].id] = j;
        }
    }

});