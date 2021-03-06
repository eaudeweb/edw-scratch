$(function() {
  $('.favourite-single, .favourite-list').on('click', function(evt) {
    evt.preventDefault();
    var star = $(this);
    var url = star.attr('href');
    $.ajax({
      type: "GET",
      url: url,
      dataType: "script",
      success: function() {
        var css_class = star.find('i').attr('class');
        if(css_class == "fa fa-lg fa-star") {
          star.find('i').attr('class', "fa fa-lg fa-star-o");
        }
        else {
          star.find('i').attr('class', "fa fa-lg fa-star");
        }
      }
    });
  });
});

$(function() {
  $('.favourite-list').on('click', function (evt) {
    evt.preventDefault();
    var row = $(this).parent().parent();
    var row_class = row.attr('class');
    if (row_class == "bg-info") {
      row.attr('class', 'bg-warning');
    }
    else {
      row.attr('class', 'bg-info');
    }
  });
});

$(function() {
  $('.favourite-single').on('click', function(evt) {
    evt.preventDefault();
    var text = $(this).find('small').text();
    if(text == 'Mark as favourite') {
      $(this).find('small').text('Remove from favourites')
    }
    else {
      $(this).find('small').text('Mark as favourite')
    }
    var div = $('table').parent();
    var div_class = div.attr('class');
    if (div_class == 'bg-info') {
      div.attr('class', 'bg-warning');
    }
    else {
      div.attr('class', 'bg-info');
    }
  });
});

$(function() {
  $('.archive-single, .archive-list').on('click', function(evt) {
    evt.preventDefault();
    var url = $(this).attr('href');
    $.ajax({
      type: "GET",
      url: url,
      dataType: "script",
      success: function() {}
    });
  });
});

$(function() {
  $('.archive-list').on('click', function (evt) {
    evt.preventDefault();
    $(this).parent().parent().remove();
  });
});

$(function() {
  $('.archive-single').on('click', function (evt) {
    evt.preventDefault();
    var text = $(this).find('small').text();
    if(text == 'Delete this tender') {
      $(this).find('small').text('Set tender as active')
    }
    else {
      $(this).find('small').text('Delete this tender')
    }
  });
});
