var manufacturers_list = undefined;
var token = Cookies.get("_xsrf");
$.ajaxSetup({
  headers: {
    "X-XSRFToken": token
  }
});

function checkForLast() {
  var divs = $("#conflicted-manufacturers").children().length;
  $("#excel-filtered-count").text(divs);
  if (divs == 0) {
    filterWithoutManufacturerCheck();
  }
}

function checkForComplete(div) {
  var ajax = div.closest(".modal-dialog").find(".modal-ajax");
  var name = ajax.find(".row-product-name").text();
  var manufacturer = ajax.find(".row-manufacturer-name").text();
  if (ajax.attr("product") == "true" && ajax.attr("manufacturer") == "true") {
    var row_id = ajax.attr("row-id");
    clean_rows(name, manufacturer);
    check_for_last_row(row_id);
    $("#create-new-product").hide();
    $("#cancel-row-editing").hide();
    $("#complete-row-editing").show();
  }
}
function filterWithoutManufacturerCheck() {
  $("#conflicted-manufacturers").html("");
  $("#manufacturer-progress").show();
  $("#second-filter").hide();
  $("#first-filter").hide();
  var data = {
    prd: prd_index,
    partial: "yes",
    key: key,
    mnf: mnf_index,
    prc: prc_index,
    exp: exp_index,
    ignore: ignore,
    row: row,
    exp_mask: $("#excel-expiry-format").val()
  };
  if (!$("#price-wire100")[0].checked) {
    data["prc_wire100_index"] = prc_wire100_index;
  } else {
    data["prc_wire100_percent"] = $("#price-wire100-percentage-input").val();
  }
  if (!$("#price-wire75")[0].checked) {
    data["prc_wire75_index"] = prc_wire75_index;
  } else {
    data["prc_wire75_percent"] = $("#price-wire75-percentage-input").val();
  }
  if (!$("#price-wire50")[0].checked) {
    data["prc_wire50_index"] = prc_wire50_index;
  } else {
    data["prc_wire50_percent"] = $("#price-wire50-percentage-input").val();
  }
  if (!$("#price-wire25")[0].checked) {
    data["prc_wire25_index"] = prc_wire25_index;
  } else {
    data["prc_wire25_percent"] = $("#price-wire25-percentage-input").val();
  }
  var request = $.ajax({
    url: "/export/parse/",
    type: "post",
    data: data,
    dataType: "json",
    error: function(data) {
      alert("error");
      $("#second-progress").hide();
      $("#first-filter").show();
    },
    success: function(data) {
      document.location = "//" + window.location.host + "/pricelist/";
    }
  });
}

function add_product_alias(agent, mid, alias, func) {
  var request = $.ajax({
    url: "/supplier/" + agent + "/aliases/product/add/",
    type: "post",
    data: { pid: mid, alias: alias },
    dataType: "json",
    error: function(data) {
      alert("error");
      $("#second-progress").hide();
      $("#first-filter").show();
    },
    success: function(data) {
      func(data);
    }
  });
}

function add_manufacturer_alias(agent, mid, alias, func) {
  var request = $.ajax({
    url: "/supplier/" + agent + "/aliases/manufacturer/add/",
    type: "post",
    data: { mid: mid, alias: alias },
    dataType: "json",
    error: function(data) {
      alert("error");
    },
    success: function(data) {
      func(data);
    }
  });
}
function parse_filtered_data(data) {
  $("#manufacturer-progress").hide();
  $("#second-progress").hide();
  var conflicted_manufacturers = data["manufacturers"];
  if (!$.isEmptyObject(conflicted_manufacturers)) {
    var html = "";
    $("#conflicted").hide();
    for (const [manufacturer, value] of Object.entries(
      conflicted_manufacturers
    )) {
      if (manufacturer == "") {
        continue;
      }
      html +=
        '<div class="card manufacturer-block bg-dark text-white m-2" ><div class="card-body pt-0"> <div class="container-fluid pl-0 pr-0"> <div class="row m-1">';
      html +=
        '<div class="col m-0 p-0 pt-3"> <h4 class="card-text">' +
        manufacturer +
        "</h4>";
      html += '<p class="ml-1">Возможно имелось ввиду:</p>';
      if (value.length > 0) {
        html += '<select class="form-control ml-1">';
        for (var i = 0; i < value.length; i++) {
          html +=
            '<option value="' +
            value[i][1]["manufacturer_id"] +
            '">' +
            value[i][0] +
            "</option>";
        }
        html += "</select>";
      }
      html +=
        '<a href="#" class="btn manual-manufacturer-link"><i class="fa fa-arrow-down"></i> Выбрать вручную</a>';
      html += '<div class="manual-manufacturer-list"></div>';
      html += "</div></div><hr/>";
      html +=
        '<div class="buttons"><div class="loading bg-dark"></div><a href="#" class="btn btn-danger m-1 manufacturer-alias-save">Сохранить алиас</a>';
      html +=
        '<a href="#" class="btn btn-primary m-1 manufacturer-alias-ignore">Новый производитель</a></div>';
      html += "</div></div></div>";
    }
    $("#conflicted-manufacturers-parent").show();
    $("#conflicted-manufacturers").html(html);
    $("#excel-filtered-count")
      .parent()
      .hide();
  } else {
    $("#conflicted").show();
    $("#excel-filtered-count")
      .parent()
      .show();
    $("#conflicted-manufacturers-parent").hide();
  }

  conflicted = data["conflicted"];

  if (conflicted.length > 0) {
    var html =
      "<table id='result_table' class='second-filter-result' border=1>";
    html +=
      "<thead><th>Товар</th><th>Производитель</th><th>Цена нал</th><th> Цена 100</th><th>Цена 75</th><th>Цена 50</th><th>Цена 25</th><th>Срок годности</th></thead>";
    html += "<tbody>";
    $("#excel-filtered-count").text(conflicted.length);
    for (var i = conflicted.length - 1; i >= 0; i--) {
      var conflict = conflicted[i];
      html += "<tr data-id='" + i + "' data-row='" + conflict["row"] + "' ";
      if (conflict["n_c"]) {
        html += " data-wrong-product='True' ";
      } else {
        html += " data-potential-manufacturer='" + conflict["m_p"] + "' ";
      }
      if (conflict["m_c"]) {
        html += " data-wrong-manufacturer='True' ";
      } else {
        html += " data-manufacturer-id='" + conflict["mid"] + "' ";
      }
      html += ">";
      html +=
        "<td><span class='value' data-name='" +
        conflict["cn"] +
        "'>" +
        conflict["n"] +
        "</span>";
      if (conflict["n_c"]) {
        html += ' <i class="fa fa-exclamation-circle"></i>';
      }
      html += "</td>";
      html += "<td><span class='value'>" + conflict["m"] + "</span>";
      if (conflict["m_c"]) {
        html += ' <i class="fa fa-exclamation-circle"></i>';
      }
      html += "</td>";
      html += "<td><span class='value'>" + conflict["price_cash"] + "</span>";
      if (conflict["p_c"]) {
        html += ' <i class="fa fa-exclamation-circle"></i>';
      }
      html += "</td>";
      var expiry = conflict["e"];
      var w100 = conflict["price_wire100"];
      if (w100 == undefined) {
        w100 = "-";
      }
      var w75 = conflict["price_wire75"];
      if (w75 == undefined) {
        w75 = "-";
      }
      var w50 = conflict["price_wire50"];
      if (w50 == undefined) {
        w50 = "-";
      }
      var w25 = conflict["price_wire25"];
      if (w25 == undefined) {
        w25 = "-";
      }
      html += "<td><span class='value'>" + w100 + "</span></td>";
      html += "<td><span class='value'>" + w75 + "</span></td>";
      html += "<td><span class='value'>" + w50 + "</span></td>";
      html += "<td><span class='value'>" + w25 + "</span></td>";
      html += "<td><span class='value'>" + expiry + "</span>";
      if (conflict["e_c"]) {
        html += ' <i class="fa fa-exclamation-circle"></i>';
      }
      html += "</td>";
    }
    html += "</tbody>";
    html += "</table>";
    $("#conflicted").html(html);
  } else {
    if ($.isEmptyObject(conflicted_manufacturers)) {
      $("#excel-filtered-count")
        .parent()
        .hide();
      $("#publish-result").show();
    }
  }
  $("#second-progress").hide();
  $("#second-filter").show();
}
function publish(agent, key, func) {
  var request = $.ajax({
    url: "/pricelist/" + key + "/export/publish/",
    type: "post",
    dataType: "json",
    error: function(data) {
      alert("error");
      $("#second-progress").hide();
      $("#first-filter").show();
    },
    success: function(data) {
      func(data);
    }
  });
}
function process(func, keep) {
  var data = {
    prd: prd_index,
    partial: false,
    key: key,
    mnf: mnf_index,
    ignore: ignore,
    prc: prc_index,
    exp: exp_index,
    load: load_index,
    quantity: quantity_index,
    row: row,
    exp_mask: $("#excel-expiry-format").val()
  };
  if (!$("#price-wire100")[0].checked) {
    data["prc_wire100_index"] = prc_wire100_index;
  } else {
    data["prc_wire100_percent"] = $("#price-wire100-percentage-input").val();
  }
  if (!$("#price-wire75")[0].checked) {
    data["prc_wire75_index"] = prc_wire75_index;
  } else {
    data["prc_wire75_percent"] = $("#price-wire75-percentage-input").val();
  }
  if (!$("#price-wire50")[0].checked) {
    data["prc_wire50_index"] = prc_wire50_index;
  } else {
    data["prc_wire50_percent"] = $("#price-wire50-percentage-input").val();
  }
  if (!$("#price-wire25")[0].checked) {
    data["prc_wire25_index"] = prc_wire25_index;
  } else {
    data["prc_wire25_percent"] = $("#price-wire25-percentage-input").val();
  }
  data["keep"] = keep;
  var request = $.ajax({
    url: "/export/parse/",
    type: "post",
    data: data,
    dataType: "json",
    error: function(data) {
      alert("error");
      $("#second-progress").hide();
      $("#first-filter").show();
    },
    success: function(data) {
      document.location = "//" + window.location.host + "/pricelist/";
    }
  });
}

function draw_manufacturers(data, container) {
  var i = +new Date();
  var id_ = "manufacturer-" + i;
  var html =
    '<input class="form-control manual-manufacturer-select" id="' +
    id_ +
    '" list="' +
    id_ +
    '-select"><datalist id="' +
    id_ +
    '-select">';
  for (const [manufacturer, value] of Object.entries(data)) {
    html += '<option data-value="' + value + '">' + manufacturer + "</select>";
  }
  html +=
    '</datalist><input type="hidden" class="manual-value" name="answer" id="' +
    id_ +
    '-hidden">';
  container.html(html);
  document.querySelector("#" + id_).addEventListener("keyup", function(e) {
    var input = e.target,
      list = input.getAttribute("list"),
      options = document.querySelectorAll("#" + list + " option"),
      hiddenInput = document.getElementById(input.id + "-hidden"),
      inputValue = input.value;

    hiddenInput.value = inputValue;

    for (var i = 0; i < options.length; i++) {
      var option = options[i];

      if (option.innerText === inputValue) {
        hiddenInput.value = option.getAttribute("data-value");
        break;
      }
    }
  });
}

function filter_disabled(obj) {
  disabled[obj.attr("id")] = obj.val();
  $(".bounded").each(function() {
    $(this)
      .find("option:disabled")
      .removeAttr("disabled");
    for (const [key, value] of Object.entries(disabled)) {
      $(this)
        .find('option[value="' + value + '"]')
        .attr("disabled", "disabled");
    }
  });
}

function load_all_manufacturers(func) {
  var request = $.ajax({
    url: "/manufacturer/list/",
    type: "get",
    dataType: "json",
    error: function(data) {
      alert("error");
    },
    success: function(data) {
      func(data);
    }
  });
}
function check_for_last_row(row_id) {
  $("#result_table")
    .find('tr[data-id="' + row_id + '"]')
    .remove();
  setTimeout(function() {
    var divs = $("#result_table tbody").find("tr").length;
    $("#excel-filtered-count").text(divs);
    var trs = $("#result_table tbody tr");
    if (trs.length > 0) {
      trs.eq(0).trigger("click");
    } else {
      $("#rowModal").modal("hide");
      $("#conflicted").hide();
      $("#publish-result").show();
    }
  }, 100);
}

function clean_rows(name, manufacturer) {
  console.log("clean ", name, manufacturer);
  $("#result_table tbody")
    .find("tr")
    .each(function() {
      if (
        $(this)
          .find("td")
          .eq(0)
          .text()
          .trim() == name &&
        $(this)
          .find("td")
          .eq(1)
          .text()
          .trim() == manufacturer
      ) {
        $(this).remove();
      }
    });
}
