package io.zershyan.examplemod.datagen.lang;

import io.zershyan.examplemod.ExampleMod;
import net.minecraft.resources.ResourceLocation;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

/** 语言数据基类，聚合各子类并统一对外提供 */
public abstract class ExampleModLang {
    private static final List<Entry> LangEntries = new ArrayList<>();
    protected final List<Entry> entries = new ArrayList<>();

    public static void stringEntry(String key, String enDesc, String zhDesc) {
        LangEntries.add(new FinalEntry<>(key, enDesc, zhDesc));
    }

    public static List<FinalEntry<?>> getAllLang() {
        List<FinalEntry<?>> entryList = new ArrayList<>();
        Stream.of( //添加lang类
                new ExampleModKeyLang(),
                new ExampleModConfigLang(),
                new ExampleModRegistryLang()
        ).map(ExampleModLang::initLang).map(
                list -> list.stream().map(Entry::toLang).toList()
        ).forEach(entryList::addAll);
        entryList.addAll(LangEntries.stream().map(Entry::toLang).toList());
        return entryList;
    }

    /** 按 ResourceLocation 生成属性描述键 */
    public static String getAttributeDesc(ResourceLocation location) {
        return location.toLanguageKey("attribute", "desc");
    }

    /** 按 ResourceLocation 生成声音字幕键 */
    public static String getSoundDesc(ResourceLocation location) {
        return location.toLanguageKey("sound", "desc");
    }

    /** 按 ResourceLocation 生成自定义注册项的描述键 */
    public static String getCustomRegistryDesc(ResourceLocation location) {
        return location.toLanguageKey("custom_registry", "desc");
    }

    protected static String getKeyDesc(String name) {
        return ExampleMod.id(name).toLanguageKey("key", "name");
    }

    protected void addEntry(Entry entry) {
        this.entries.add(entry);
    }

    protected <T> void addFinalEntry(T key, String enUs, String zhCn) {
        this.entries.add(new FinalEntry<>(key, enUs, zhCn));
    }

    private List<Entry> initLang() {
        init(); // 无返回初始化
        return init(entries); // 有返回初始化
    }

    protected List<Entry> init(List<Entry> entries) {
        return entries;
    }

    protected void init() {
    }

    public interface Entry {
        FinalEntry<?> toLang();
    }

    public record Lang(String enUs, String zhCn) {
    }

    public record FinalEntry<T>(T key, Lang lang) implements Entry {
        public FinalEntry(T key, String enDesc, String zhDesc) {
            this(key, new Lang(enDesc, zhDesc));
        }

        @Override
        public FinalEntry<?> toLang() {
            return this;
        }
    }
}
