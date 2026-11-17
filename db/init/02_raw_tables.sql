create table raw.venues (
    venue_id               serial primary key,
    name                   text not null,
    city                   text,
    intended_event         text not null,
    capacity               int,
    overage_fee_per_guest  numeric(10,2),
    allows_outside_caterer boolean,
    allows_baraat          boolean,
    allows_open_flame      boolean,
    noise_curfew           time,
    alcohol_policy         text,
    created_at             timestamp not null default now(),
    updated_at             timestamp not null default now()
);

create table raw.vendors (
    vendor_id  serial primary key,
    name       text not null,
    category   text not null,
    city       text,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
);

create table raw.quotes (
    quote_id     serial primary key,
    venue_id     int references raw.venues(venue_id),
    vendor_id    int references raw.vendors(vendor_id),
    event_name   text not null,
    guest_count  int not null,
    status       text not null,
    quoted_total numeric(12,2) not null,
    created_at   timestamp not null default now(),
    updated_at   timestamp not null default now(),
    check (num_nonnulls(venue_id, vendor_id) = 1)
);

create table raw.quote_line_items (
    line_item_id serial primary key,
    quote_id     int not null references raw.quotes(quote_id),
    item_type    text not null,
    description  text,
    unit_price   numeric(12,2) not null,
    quantity     numeric(10,2) not null default 1,
    amount       numeric(12,2) not null,
    updated_at   timestamp not null default now()
);
